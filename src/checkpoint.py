import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock


class CheckpointStore:
    """Durable per-shot state for safe resume after interruption."""

    def __init__(self, path: str = "output/checkpoint.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "shots": {}}
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self) -> None:
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=2)
        temp.replace(self.path)

    def get(self, shot_id: str) -> dict:
        return self.data.get("shots", {}).get(str(shot_id), {})

    def update(self, shot_id: str, **values) -> dict:
        with self._lock:
            shots = self.data.setdefault("shots", {})
            state = shots.setdefault(str(shot_id), {})
            state.update(values)
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save()
            return state

    def mark_submitted(self, shot_id: str, external_task_id: str) -> dict:
        return self.update(
            shot_id,
            status="submitted",
            external_task_id=external_task_id,
            error=None,
        )

    def mark_succeeded(self, shot_id: str, task: dict) -> dict:
        return self.update(
            shot_id,
            status="succeeded",
            kling_task_id=task.get("id"),
            outputs=task.get("outputs", []),
            error=None,
        )

    def mark_downloaded(self, shot_id: str, output_path: str) -> dict:
        return self.update(shot_id, status="downloaded", output_path=output_path)

    def mark_failed(self, shot_id: str, error: str) -> dict:
        state = self.get(shot_id)
        return self.update(
            shot_id,
            status="failed",
            attempts=int(state.get("attempts", 0)) + 1,
            error=error,
        )

    def is_downloaded(self, shot_id: str) -> bool:
        state = self.get(shot_id)
        path = state.get("output_path")
        return state.get("status") == "downloaded" and bool(path) and Path(path).exists()
