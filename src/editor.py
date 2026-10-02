import subprocess
from pathlib import Path

def concat_clips(clips: list[str], output: str) -> None:
    """Concatenate compatible clips with FFmpeg concat demuxer."""
    if not clips:
        raise ValueError("No clips supplied")
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest = out.parent / "concat.txt"
    manifest.write_text("\n".join(f"file '{Path(c).resolve()}'" for c in clips), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(manifest), "-c", "copy", str(out)
    ], check=True)
