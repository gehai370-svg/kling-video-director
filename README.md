# Kling Video Director

AI 视频自动生产流水线：创意/文案/素材 → 分镜 → Kling Prompt → 文生/图生自动路由 → Kling 3.0 Turbo → 任务轮询 → 断点续跑 → 下载镜头 → FFmpeg 合成 MP4。

## 已实现

Kling 3.0 Turbo 文生视频与首帧图生视频、Bearer API Key、任务轮询与批量分页、视频下载、每镜头 checkpoint、已提交任务恢复、失败镜头独立重试、文生/图生自动路由，以及 FFmpeg 最终合成。

## Quick start

需要 Python 3.10+ 与 FFmpeg。复制 .env.example 为 .env，填写 KLING_API_KEY，然后编辑 examples/project.json。

只生成分镜：

    python -m src.main examples/project.json --plan-only

一键生成完整视频：

    python -m src.main examples/project.json

输出位于 output/<project_id>/：storyboard.json、checkpoint.json、clips/ 和 final.mp4。

再次执行同一个项目时会读取 checkpoint：已经下载的镜头跳过；已提交任务继续查询；成功但未下载的任务继续下载；失败或未开始镜头才重新生成。

## 自定义分镜

项目 JSON 可以加入 storyboard 数组。每个镜头可提供 prompt、description、image_url、duration、resolution 和 aspect_ratio。存在 image_url 时自动走图生视频，否则走文生视频。

不要把 Kling API Key 提交到 GitHub；.env 已被 .gitignore 忽略。

## 下一阶段

当前导演模块提供确定性的分镜骨架。下一阶段可接入任意 LLM，让一个主题或文案自动生成真正的脚本、镜头语言、镜头时长和专业 Kling Prompt，而不把工作流锁定在单一模型供应商。
