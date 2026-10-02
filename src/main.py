import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

from .ai_director import create_director_plan
from .director_schema import validate_director_plan
from .editor import concat_clips
from .prompt_engine import kling_prompt
from .resumable_runner import ResumableKlingRunner


def prepare_storyboard(project: dict) -> list[dict]:
    explicit = project.get("storyboard")
    if isinstance(explicit, list) and explicit:
        shots = validate_director_plan({"shots": explicit}, project)
        for shot in shots:
            if not shot.get("prompt"):
                shot["prompt"] = kling_prompt(shot, project)
        return shots
    return create_director_plan(project)


def run_pipeline(project_path: str, plan_only: bool = False) -> Path:
    load_dotenv()
    project = json.loads(Path(project_path).read_text(encoding="utf-8"))
    project_slug = project.get("project_id") or Path(project_path).stem
    root = Path("output") / project_slug
    clips_dir = root / "clips"
    root.mkdir(parents=True, exist_ok=True)

    shots = prepare_storyboard(project)
    storyboard_path = root / "storyboard.json"
    storyboard_path.write_text(
        json.dumps({"project": project, "shots": shots}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Storyboard: {storyboard_path}")

    if plan_only:
        return storyboard_path

    runner = ResumableKlingRunner(
        checkpoint_path=str(root / "checkpoint.json"),
        clips_dir=str(clips_dir),
        max_attempts=int(project.get("max_attempts", 3)),
    )
    clips = runner.run_all(shots)

    missing = [clip for clip in clips if not Path(clip).exists()]
    if missing:
        raise RuntimeError(f"Cannot assemble video; missing clips: {missing}")

    final_path = root / project.get("output_filename", "final.mp4")
    concat_clips(clips, str(final_path))
    print(f"Final video: {final_path}")
    return final_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Kling Video Director V2 pipeline")
    parser.add_argument("project", help="Project JSON file")
    parser.add_argument("--plan-only", action="store_true", help="Create storyboard/prompts only; do not call Kling.")
    args = parser.parse_args()
    run_pipeline(args.project, plan_only=args.plan_only)


if __name__ == "__main__":
    main()
