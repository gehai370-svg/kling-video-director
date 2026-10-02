def kling_prompt(shot: dict, project: dict) -> str:
    parts = [
        shot.get("description", ""),
        f"Camera: {shot.get('camera', '')}.",
        f"Motion: {shot.get('motion', '')}.",
        f"Lighting/style: {shot.get('lighting', project.get('style', 'cinematic'))}.",
        f"Aspect ratio: {project.get('aspect_ratio', '9:16')}.",
        "High visual consistency, natural motion, coherent anatomy, cinematic detail."
    ]
    return " ".join(p for p in parts if p)
