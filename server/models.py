from pydantic import BaseModel
from typing import List, Optional

class SlideSpec(BaseModel):
    title: str
    bullets: List[str]
    notes: Optional[str] = None
    layout_hint: Optional[str] = None

class Outline(BaseModel):
    estimated_slide_count: int
    slides: List[SlideSpec]
    tone: Optional[str] = None
