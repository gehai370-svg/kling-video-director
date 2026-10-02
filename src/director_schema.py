from dataclasses import dataclass
from typing import Any


ALLOWED_SHOT_TYPES = {"text_to_video", "image_to_video"}


def validate_director_plan(plan: dict[str, Any], project: dict[str, Any]) -> list[dict]:
    shots = plan.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("Director plan must contain a non-empty shots array")

    target_ratio = project.get("aspect_ratio", "9:16")
    validated = []
    for index, raw in enumerate(shots, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Shot {index} must be an object")

        shot = dict(raw)
        shot["id"] = str(shot.get("id", index))
        shot["index"] = index
        shot["description"] = str(shot.get("description", "")).strip()
        shot["camera"] = str(shot.get("camera", "")).strip()
        shot["motion"] = str(shot.get("motion", "")).strip()
        shot["lighting"] = str(shot.get("lighting", "")).strip()
        shot["sound"] = str(shot.get("sound", "")).strip()
        shot["prompt"] = str(shot.get("prompt", "")).strip()
        shot["aspect_ratio"] = str(shot.get("aspect_ratio", target_ratio))

        image_url = shot.get("image_url") or shot.get("reference_image")
        shot["image_url"] = image_url

        generation_mode = shot.get("generation_mode")
        if generation_mode not in ALLOWED_SHOT_TYPES:
            generation_mode = "image_to_video" if image_url else "text_to_video"
        if generation_mode == "image_to_video" and not image_url:
            generation_mode = "text_to_video"
        shot["generation_mode"] = generation_mode

        if not shot["description"] and not shot["prompt"]:
            raise ValueError(f"Shot {index} needs description or prompt")

        # Keep API-supported defaults conservative. Kling client remains source of truth.
        duration = shot.get("duration")
        if duration is not None:
            shot["duration"] = int(round(float(duration)))

        validated.append(shot)

    return validated
