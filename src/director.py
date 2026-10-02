def build_storyboard(project: dict) -> list[dict]:
    """Deterministic V1 storyboard scaffold. Replace/extend with an LLM director later."""
    count = max(1, int(project.get("shots", 6)))
    total = float(project.get("duration_seconds", 30))
    duration = round(total / count, 2)
    idea = project["idea"]
    style = project.get("style", "cinematic")
    shots = []
    for i in range(count):
        shots.append({
            "index": i + 1,
            "duration": duration,
            "description": f"{idea} — visual beat {i + 1}/{count}",
            "camera": "cinematic camera movement",
            "motion": "natural subject and environmental motion",
            "lighting": style,
        })
    return shots
