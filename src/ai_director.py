import json
from typing import Protocol, Any

from .director import build_storyboard
from .director_schema import validate_director_plan
from .prompt_engine import kling_prompt


SYSTEM_PROMPT = """You are a commercial film director, cinematographer, storyboard artist,
AI video prompt engineer and editor. Convert a creative brief into an executable shot plan.

Return JSON only. Build a coherent sequence rather than isolated pretty shots.
For every shot define: description, camera, motion, lighting, sound, generation_mode,
duration, aspect_ratio and a production-ready Kling prompt.

Directing rules:
- Give every shot a clear narrative purpose and visible action.
- Preserve subject, wardrobe, product, environment and lighting continuity.
- Use intentional shot-size progression and motivated camera movement.
- Describe physical motion concretely; avoid vague hype words.
- Prompts must describe what the camera sees and how it moves.
- Use image_to_video only when an image_url/reference_image is actually supplied.
- Otherwise use text_to_video.
- Do not invent unsupported Kling API parameters.
"""


class DirectorProvider(Protocol):
    def create_plan(self, project: dict[str, Any]) -> dict[str, Any]:
        ...


class DeterministicDirector:
    """Offline fallback. It never calls an external LLM."""

    def create_plan(self, project: dict[str, Any]) -> dict[str, Any]:
        shots = build_storyboard(project)
        for shot in shots:
            shot["generation_mode"] = (
                "image_to_video" if shot.get("image_url") or shot.get("reference_image")
                else "text_to_video"
            )
            shot["sound"] = ""
            shot["aspect_ratio"] = project.get("aspect_ratio", "9:16")
            shot["prompt"] = kling_prompt(shot, project)
        return {"shots": shots}


def director_request(project: dict[str, Any]) -> dict[str, str]:
    """Portable request payload for any JSON-capable LLM provider."""
    brief = {
        "title": project.get("title"),
        "idea": project.get("idea"),
        "duration_seconds": project.get("duration_seconds", 30),
        "aspect_ratio": project.get("aspect_ratio", "9:16"),
        "style": project.get("style", "cinematic"),
        "language": project.get("language", "zh-CN"),
        "shot_count": project.get("shots", 6),
        "assets": project.get("assets", []),
        "requirements": project.get("requirements", []),
    }
    return {
        "system": SYSTEM_PROMPT,
        "user": json.dumps(brief, ensure_ascii=False, indent=2),
    }


def create_director_plan(project: dict[str, Any], provider: DirectorProvider | None = None) -> list[dict]:
    engine = provider or DeterministicDirector()
    plan = engine.create_plan(project)
    shots = validate_director_plan(plan, project)

    # Ensure a usable Kling prompt even if a provider leaves prompt empty.
    for shot in shots:
        if not shot.get("prompt"):
            shot["prompt"] = kling_prompt(shot, project)
    return shots
