# server/text_mapper.py
import re
from typing import Dict, Any, List

def map_text_to_outline(text: str, guidance: str) -> Dict[str, Any]:
    """
    Heuristic fallback: split input into blocks and create titles + bullets.
    Returns: { estimated_slide_count, slides: [{title, bullets, notes?}] }
    """
    # Split by double newlines or by markdown headings
    blocks = re.split(r'\n{2,}', text.strip())
    slides: List[Dict[str, Any]] = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        # If markdown heading present, use as title
        m = re.match(r'^(?:#+)\s*(.+)', b)
        if m:
            title = m.group(1).strip()
            body = re.sub(r'^(?:#+)\s*.*\n?', '', b).strip()
        else:
            # first sentence or first line as title
            parts = re.split(r'\n|\.', b, maxsplit=1)
            title = parts[0].strip()[:80] or 'Slide'
            body = parts[1].strip() if len(parts) > 1 else ''

        bullets = [s.strip() for s in re.split(r'\n|-|•|—', body) if s.strip()]
        if not bullets and body:
            # split into sentences if no line bullets
            bullets = [s.strip() for s in re.split(r'\.\s+', body) if s.strip()]

        bullets = bullets[:6]
        slides.append({'title': title, 'bullets': bullets})

    # cap slides
    if len(slides) > 30:
        slides = slides[:30]

    return {'estimated_slide_count': len(slides), 'slides': slides, 'tone': guidance or 'default'}
