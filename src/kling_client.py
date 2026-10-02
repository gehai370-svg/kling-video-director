import os
import requests


class KlingClient:
    """Kling AI Open Platform client for Kling 3.0 Turbo image-to-video."""

    DEFAULT_BASE_URL = "https://api-singapore.klingai.com"
    IMAGE_TO_VIDEO_PATH = "/image-to-video/kling-3.0-turbo"

    def __init__(self):
        self.base_url = os.getenv("KLING_BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key = os.getenv("KLING_API_KEY", "")
        self.status_path = os.getenv("KLING_STATUS_PATH", "")

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
        contents = [
            {"type": "prompt", "text": prompt},
            {"type": "first_frame", "url": first_frame_url},
        ]
        payload = {
            "contents": contents,
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

    def get_task(self, task_id: str) -> dict:
        """Task-query endpoint is configurable until its official path is added."""
        if not self.status_path:
            raise RuntimeError(
                "KLING_STATUS_PATH is not configured. Add the official task-query path from Kling docs."
            )
        url = self.base_url + self.status_path.format(task_id=task_id)
        response = requests.get(url, headers=self.headers, timeout=60)
        response.raise_for_status()
        return response.json()
