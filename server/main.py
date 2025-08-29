# server/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO

from server.llm_adapter import summarize_to_outline
from server.text_mapper import map_text_to_outline
from server.slide_builder import build_presentation_from_outline
from server.dependencies import MAX_TEMPLATE_SIZE

app = FastAPI(title='SlideGenius Backend')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

@app.post('/api/outline')
async def outline_endpoint(
    text: str = Form(...),
    guidance: str = Form(''),
    provider: str = Form('openai'),
    api_key: str = Form(...)
):
    # Call LLM (user-provided key); fallback to heuristics
    outline = summarize_to_outline(text, guidance, provider, api_key)
    if not outline or 'slides' not in outline:
        outline = map_text_to_outline(text, guidance)
    return JSONResponse(outline)

@app.post('/api/generate')
async def generate_endpoint(
    text: str = Form(...),
    guidance: str = Form(''),
    provider: str = Form('openai'),
    api_key: str = Form(...),
    template: UploadFile = File(...)
):
    # basic validation
    if not template.filename.lower().endswith(('.pptx', '.potx')):
        raise HTTPException(status_code=400, detail='Upload a .pptx or .potx file')

    contents = await template.read()
    if len(contents) > MAX_TEMPLATE_SIZE:
        raise HTTPException(status_code=400, detail=f'Template too large; max {MAX_TEMPLATE_SIZE} bytes')

    # get outline via LLM with provided key
    outline = summarize_to_outline(text, guidance, provider, api_key)
    if not outline or 'slides' not in outline:
        outline = map_text_to_outline(text, guidance)

    out = BytesIO()
    build_presentation_from_outline(contents, outline, out)
    out.seek(0)
    headers = {'Content-Disposition': 'attachment; filename=SlideGenius_Output.pptx'}
    return StreamingResponse(out, media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation', headers=headers)
