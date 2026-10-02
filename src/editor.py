import subprocess
from pathlib import Path

def _escape_concat_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "'\\''")

def concat_clips(clips: list[str], output: str) -> None:
    if not clips:
        raise ValueError("No clips supplied")
    paths = [Path(c) for c in clips]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing clips: {missing}")
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest = out.parent / "concat.txt"
    manifest.write_text("\n".join(f"file '{_escape_concat_path(p)}'" for p in paths), encoding="utf-8")
    copy_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c", "copy", str(out)]
    try:
        subprocess.run(copy_cmd, check=True)
        return
    except subprocess.CalledProcessError:
        pass
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", str(out)], check=True)
