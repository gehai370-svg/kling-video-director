import argparse
import uuid
from pathlib import Path
from dotenv import load_dotenv
from .kling_client import KlingClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one Kling 3.0 Turbo image-to-video clip.")
    parser.add_argument("--image-url", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--resolution", default="1080p")
    parser.add_argument("--output", default="output/clips/generated.mp4")
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    load_dotenv()
    client = KlingClient()
    external_id = f"kvd-{uuid.uuid4().hex}"

    created = client.create_image_to_video(
        prompt=args.prompt,
        first_frame_url=args.image_url,
        duration=args.duration,
        resolution=args.resolution,
        external_task_id=external_id,
    )
    print(f"Submitted Kling task: {external_id}")
    task = client.wait_for_task(
        external_id,
        poll_seconds=args.poll_seconds,
        timeout_seconds=args.timeout,
    )
    path = client.download_video(task, args.output)
    print(f"Video saved to {Path(path)}")


if __name__ == "__main__":
    main()
