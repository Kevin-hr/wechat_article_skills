---
name: ComfyUI 图像生成
description: 调用 ComfyUI API 生成图像，支持批量生成分镜图和管理工作流模板。使用场景包括：(1) 从 sora-2-data.js 批量生成 Sora-2 项目分镜图；(2) 调用 ComfyUI 执行自定义工作流；(3) 保存/加载工作流 JSON 文件；(4) 任何图片生成任务。出图、生成 ComfyUI 图像、调用 ComfyUI API、批量生成分镜图、执行完整任务等指令触发此技能。
---

# ComfyUI 图像生成

## 快速开始

### 批量生成分镜图

```bash
python scripts/generate_comfyui_images.py --data-file ../../sora-2-data.js
```

### 自定义工作流出图

```bash
python scripts/comfyui_client.py --workflow assets/workflow.json --server-url http://127.0.0.1:8188
```

### 管理工作流

```bash
# 保存当前工作流
python scripts/workflow_manager.py save --name my_workflow --workflow assets/workflow.json

# 列出所有工作流
python scripts/workflow_manager.py list

# 加载工作流
python scripts/workflow_manager.py load --name my_workflow --output loaded_workflow.json
```

## 工作流模板

| 模板 | 说明 |
|------|------|
| `assets/default_workflow.json` | 默认 SD3 基础工作流 |
| `assets/image_to_image.json` | 图生图工作流 |

## 脚本说明

### generate_comfyui_images.py
从 sora-2-data.js 批量生成分镜图。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--server-url` | http://127.0.0.1:8188 | ComfyUI 服务器地址 |
| `--output-dir` | ./comfyui_outputs | 输出目录 |
| `--data-file` | sora-2-data.js | 数据文件路径 |
| `--prompt-type` | t2i_core | 提示词类型 (t2i_core/midjourney) |

### comfyui_client.py
通用 ComfyUI 客户端，调用任意工作流。

| 参数 | 说明 |
|------|------|
| `--workflow` | 工作流 JSON 文件路径 |
| `--server-url` | ComfyUI 服务器地址 |
| `--output` | 输出图像路径 |
| `--seed` | 随机种子（可选） |

### workflow_manager.py
工作流模板管理工具。

| 命令 | 说明 |
|------|------|
| `save --name xxx --workflow path.json` | 保存工作流 |
| `list` | 列出所有工作流 |
| `load --name xxx --output path.json` | 加载工作流 |
| `delete --name xxx` | 删除工作流 |

## API 参考

详见 [API_REFERENCE.md](references/API_REFERENCE.md)

## 工作流模板

详见 [WORKFLOW_TEMPLATES.md](references/WORKFLOW_TEMPLATES.md)
