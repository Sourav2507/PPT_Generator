# server/llm_adapter.py
import json
from typing import Dict, Any

# We implement LLM call using the user-supplied key.
# (Currently supports OpenAI, can be extended to Anthropic/Gemini.)
def summarize_to_outline(text: str, guidance: str, provider: str, api_key: str) -> Dict[str, Any]:
    """
    Calls the specified provider (currently OpenAI) using the provided api_key.
    Returns a dict with keys: slides (list), estimated_slide_count, tone (optional).
    On any error or if provider unsupported, returns {} so caller falls back to heuristics.
    """
    # Basic prompt - ask for JSON output
    prompt = f"""
You are a slide outline generator. Convert the input text into a JSON outline for slides.
Be concise. Aim for a reasonable slide count (6–18) unless guidance requests otherwise.

Input text:

{text}

Guidance: {guidance or 'none'}

Return EXACTLY parseable JSON with:
- slides: array of objects {{ "title": str, "bullets": [str], "notes"?: str }}
- estimated_slide_count: int
- tone: optional string

No commentary, only JSON.
    """.strip()

    if provider.lower().startswith("openai"):
        try:
            import openai

            # Save old API key (if any), then override with user-supplied key
            old_key = getattr(openai, "api_key", None)
            openai.api_key = api_key

            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # use available model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1000,
            )

            # Extract content
            content = None
            if resp and "choices" in resp and len(resp["choices"]) > 0:
                ch = resp["choices"][0]
                if isinstance(ch.get("message"), dict):
                    content = ch["message"].get("content")
                else:
                    content = ch.get("text")

            if not content:
                return {}

            # Try parsing as JSON
            try:
                outline = json.loads(content.strip())
                if isinstance(outline, dict) and "slides" in outline:
                    return outline
                return {}
            except json.JSONDecodeError:
                # Try extracting JSON substring
                start, end = content.find("{"), content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    maybe = content[start : end + 1]
                    try:
                        outline = json.loads(maybe)
                        if "slides" in outline:
                            return outline
                    except Exception:
                        pass
                return {}
            finally:
                # Restore old API key
                if old_key is None:
                    try:
                        delattr(openai, "api_key")
                    except Exception:
                        openai.api_key = None
                else:
                    openai.api_key = old_key
        except Exception:
            return {}

    # Unsupported provider
    return {}
