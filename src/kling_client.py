import os
import time
import requests


class KlingClient:
    """Kling AI Open Platform client for Kling 3.0 Turbo image-to-video."""

    DEFAULT_BASE_URL = "https://api-singapore.klingai.com"
    IMAGE_TO_VIDEO_PATH = "/image-to-video/kling-3.0-turbo"
    TASKS_PATH = "/tasks"

    def __init__(self):
        self.base_url = os.getenv("KLING_BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key = os.getenv("KLING_API_KEY", "")

    @property
    def headers(self) -> dict:
        if not self.api_key:
            raise RuntimeError("KLING_API_KEY is not configured.")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def create_image_to_video(
        self,
        prompt: str,
        first_frame_url: str,
        duration: int = 10,
        resolution: str = "1080p",
        callback_url: str | None = None,
        external_task_id: str = "",
        watermark: bool = False,
    ) -> dict:
        payload = {
            "contents": [
                {"type": "prompt", "text": prompt},
                {"type": "first_frame", "url": first_frame_url},
            ],
            "settings": {
                "resolution": resolution,
                "duration": duration,
            },
            "options": {
                "external_task_id": external_task_id,
                "watermark_info": {"enabled": watermark},
            },
        }
        if callback_url:
            payload["options"]["callback_url"] = callback_url

        response = requests.post(
            self.base_url + self.IMAGE_TO_VIDEO_PATH,
            json=payload,
            headers=self.headers,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def get_tasks_by_external_id(self, external_task_id: str) -> dict:
        response = requests.get(
            self.base_url + self.TASKS_PATH,
            params={"external_task_ids": external_task_id},
            headers=self.headers,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _extract_task(payload: dict) -> dict:
        data = payload.get("data")
        if isinstance(data, list):
            return data[0] if data else {}
        if isinstance(data, dict):
            # Support both a direct task object and common list wrappers.
            for key in ("tasks", "items", "list"):
                value = data.get(key)
                if isinstance(value, list):
                    return value[0] if value else {}
            return data
        return {}

    def wait_for_task(
        self,
        external_task_id: str,
        poll_seconds: int = 10,
        timeout_seconds: int = 1800,
    ) -> dict:
        """Poll until Kling reports succeeded/failed or timeout is reached."""
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            payload = self.get_tasks_by_external_id(external_task_id)
            if payload.get("code") not in (None, 0):
                raise RuntimeError(
                    f"Kling API error {payload.get('code')}: {payload.get('message', '')}"
                )

            task = self._extract_task(payload)
            status = task.get("status")
            if status == "succeeded":
                return task
            if status == "failed":
                raise RuntimeError(f"Kling task failed: {task}")
            if status not in (None, "submitted", "processing"):
                raise RuntimeError(f"Unknown Kling task status: {status}")

            time.sleep(poll_seconds)

        raise TimeoutError(
            f"Kling task {external_task_id} did not finish within {timeout_seconds}s"
        )
