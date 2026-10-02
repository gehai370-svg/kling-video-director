import argparse
import uuid
from pathlib import Path
from dotenv import load_dotenv
from .kling_client import KlingClient


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Kling 3.0 Turbo clip using text-to-video or image-to-video."
    )
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--image-url", help="Optional first frame. If supplied, image-to-video is used.")
    parser.add_argument("--duration", type=int, default=None)
    parser.add_argument("--resolution", default=None)
    parser.add_argument("--aspect-ratio", default="9:16")
    parser.add_argument("--output", default="output/clips/generated.mp4")
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--watermark", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    client = KlingClient()
    external_id = f"kvd-{uuid.uuid4().hex}"

    if args.image_url:
        created = client.create_image_to_video(
            prompt=args.prompt,
            first_frame_url=args.image_url,
            duration=args.duration or 10,
            resolution=args.resolution or "1080p",
            external_task_id=external_id,
            watermark=args.watermark,
        )
        mode = "image-to-video"
    else:
        created = client.create_text_to_video(
            prompt=args.prompt,
            duration=args.duration or 3,
            resolution=args.resolution or "720p",
            aspect_ratio=args.aspect_ratio,
            external_task_id=external_id,
            watermark=args.watermark,
        )
        mode = "text-to-video"

    if created.get("code") not in (None, 0):
        raise RuntimeError(
            f"Kling create-task error {created.get('code')}: {created.get('message', '')}"
        )

    print(f"Submitted Kling {mode} task: {external_id}")
    task = client.wait_for_task(
        external_id,
        poll_seconds=args.poll_seconds,
        timeout_seconds=args.timeout,
    )
    path = client.download_video(task, args.output)
    print(f"Video saved to {Path(path)}")


if __name__ == "__main__":
    main()
