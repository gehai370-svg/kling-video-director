# Kling Video Director

通用 AI 视频导演工作流：把创意、文案、图片或首尾帧转成结构化分镜与 Kling 生成任务，并为后续自动剪辑提供统一输出。

## V1 workflow

1. Creative brief
2. Director plan
3. Storyboard JSON
4. Kling prompts
5. Kling API adapter
6. Task polling / retry
7. Download clips
8. FFmpeg assembly

## Quick start

1. Copy `.env.example` to `.env`
2. Fill in your Kling API credentials and endpoint values from your account/API documentation
3. Edit `examples/project.json`
4. Run `python -m src.main examples/project.json`

> The Kling adapter is intentionally configurable: API endpoints and authentication can change, so credentials and endpoint paths are not hard-coded.
