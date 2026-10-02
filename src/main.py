import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from .director import build_storyboard
from .prompt_engine import kling_prompt

def main(path: str) -> None:
    load_dotenv()
    project = json.loads(Path(path).read_text(encoding="utf-8"))
    shots = build_storyboard(project)
    for shot in shots:
        shot["prompt"] = kling_prompt(shot, project)
    out = Path("output")
    out.mkdir(exist_ok=True)
    target = out / "storyboard.json"
    target.write_text(json.dumps({"project": project, "shots": shots}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Storyboard written to {target}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m src.main examples/project.json")
    main(sys.argv[1])
