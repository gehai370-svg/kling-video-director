import os
import requests

class KlingClient:
    """Configurable adapter. Set endpoint/auth values according to your Kling API account docs."""

    def __init__(self):
        self.base_url = os.getenv("KLING_BASE_URL", "").rstrip("/")
        self.access_key = os.getenv("KLING_ACCESS_KEY", "")
        self.secret_key = os.getenv("KLING_SECRET_KEY", "")
        self.create_path = os.getenv("KLING_CREATE_PATH", "")
        self.status_path = os.getenv("KLING_STATUS_PATH", "")

    def configured(self) -> bool:
        return bool(self.base_url and self.access_key and self.create_path)

    def create_video(self, payload: dict) -> dict:
        if not self.configured():
            raise RuntimeError("Kling API is not configured. Fill .env using your official API credentials/docs.")
        # Authentication varies by API version/provider. Add the exact signing/header scheme here.
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.base_url + self.create_path, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> dict:
        if not self.status_path:
            raise RuntimeError("KLING_STATUS_PATH is not configured.")
        url = self.base_url + self.status_path.format(task_id=task_id)
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()
