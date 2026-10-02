import os
from dotenv import load_dotenv

from .kling_client import KlingClient


def main() -> None:
    load_dotenv()
    key = os.getenv("KLING_API_KEY", "")
    if not key:
        raise SystemExit("FAIL: KLING_API_KEY was not loaded from .env")

    print(f"Base URL: {os.getenv('KLING_BASE_URL', KlingClient.DEFAULT_BASE_URL)}")
    print(f"API key loaded: yes (length={len(key)}, prefix_ok={key.startswith('api-key-kling-')})")
    print("Checking Kling authentication without creating a video task...")

    try:
        payload = KlingClient().check_auth()
    except Exception as exc:
        raise SystemExit(f"FAIL: {exc}")

    code = payload.get("code")
    message = payload.get("message", "")
    request_id = payload.get("request_id", "")
    print(f"OK: Kling accepted the credential. code={code}, message={message}, request_id={request_id}")


if __name__ == "__main__":
    main()
