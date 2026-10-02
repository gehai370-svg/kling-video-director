from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Shot:
    index: int
    duration: float
    description: str
    camera: str = ""
    motion: str = ""
    lighting: str = ""
    prompt: str = ""
    negative_prompt: str = ""
    reference_image: Optional[str] = None

@dataclass
class VideoProject:
    title: str
    idea: str
    duration_seconds: int = 30
    aspect_ratio: str = "9:16"
    style: str = "cinematic"
    language: str = "zh-CN"
    shots: List[Shot] = field(default_factory=list)
