import uuid
from pathlib import Path

from .checkpoint import CheckpointStore
from .kling_client import KlingClient


class ResumableKlingRunner:
    """Runs storyboard shots without regenerating completed clips."""

    def __init__(
        self,
        client: KlingClient | None = None,
        checkpoint_path: str = "output/checkpoint.json",
        clips_dir: str = "output/clips",
        max_attempts: int = 3,
    ):
        self.client = client or KlingClient()
        self.store = CheckpointStore(checkpoint_path)
        self.clips_dir = Path(clips_dir)
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.max_attempts = max_attempts

    def run_shot(self, shot_id: str, prompt: str, image_url: str | None = None,
                 duration: int | None = None, resolution: str | None = None,
                 aspect_ratio: str = "9:16") -> str:
        shot_id = str(shot_id)
        if self.store.is_downloaded(shot_id):
            return self.store.get(shot_id)["output_path"]

        state = self.store.get(shot_id)
        external_id = state.get("external_task_id")

        try:
            # Resume an already-submitted task instead of paying to submit it again.
            if state.get("status") in ("submitted", "processing") and external_id:
                task = self.client.wait_for_task(external_id)
            elif state.get("status") == "succeeded" and state.get("outputs"):
                task = {
                    "id": state.get("kling_task_id"),
                    "status": "succeeded",
                    "outputs": state["outputs"],
                }
            else:
                if int(state.get("attempts", 0)) >= self.max_attempts:
                    raise RuntimeError(f"Shot {shot_id} exceeded max attempts.")

                external_id = f"kvd-{shot_id}-{uuid.uuid4().hex}"
                if image_url:
                    created = self.client.create_image_to_video(
                        prompt=prompt,
                        first_frame_url=image_url,
                        duration=duration or 10,
                        resolution=resolution or "1080p",
                        external_task_id=external_id,
                    )
                else:
                    created = self.client.create_text_to_video(
                        prompt=prompt,
                        duration=duration or 3,
                        resolution=resolution or "720p",
                        aspect_ratio=aspect_ratio,
                        external_task_id=external_id,
                    )
                if created.get("code") not in (None, 0):
                    raise RuntimeError(
                        f"Kling create error {created.get('code')}: {created.get('message', '')}"
                    )
                self.store.mark_submitted(shot_id, external_id)
                task = self.client.wait_for_task(external_id)

            self.store.mark_succeeded(shot_id, task)
            output_path = str(self.clips_dir / f"{int(shot_id):03d}.mp4")
            self.client.download_video(task, output_path)
            self.store.mark_downloaded(shot_id, output_path)
            return output_path

        except Exception as exc:
            self.store.mark_failed(shot_id, str(exc))
            raise

    def run_all(self, shots: list[dict]) -> list[str]:
        outputs = []
        for index, shot in enumerate(shots, start=1):
            shot_id = str(shot.get("id", index))
            outputs.append(
                self.run_shot(
                    shot_id=shot_id,
                    prompt=shot["prompt"],
                    image_url=shot.get("image_url"),
                    duration=shot.get("duration"),
                    resolution=shot.get("resolution"),
                    aspect_ratio=shot.get("aspect_ratio", "9:16"),
                )
            )
        return outputs
