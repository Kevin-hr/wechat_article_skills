---
name: wechat-image-recognizer
description: 图像识别与分析工具。支持多模型（GPT-4 Vision、Gemini、Claude Vision），可识别图片内容、提取文字（OCR）、分析图表、生成描述。当用户说"识别图片"、"分析这张图"、"图片里有什么"时使用。
---

# 图像识别器

## 支持的模型

| 模型 | 特点 |
|------|------|
| GPT-4 Vision | 准确度高，支持复杂场景 |
| Gemini 1.5 Pro | 长上下文，支持多图 |
| Claude 3 Vision | 细致的视觉分析 |

## 快速使用

```bash
cd .claude/skills/wechat-image-recognizer/scripts

# 识别图片并描述
python recognize.py --input image.png --model gpt

# OCR 提取文字
python recognize.py --input screenshot.png --task ocr

# 分析图表数据
python recognize.py --input chart.png --task analyze

# 微信风格描述
python recognize.py --input cover.png --task wechat
```

## 脚本参数

| 参数 | 说明 |
|------|------|
| `--input`, `-i` | 输入图片路径（必需） |
| `--model`, `-m` | 模型 (gpt/gemini/claude/deepseek) |
| `--task`, `-t` | 任务 (describe/ocr/analyze/wechat) |
| `--output`, `-o` | 输出文件路径 |
| `--style` | 输出风格 (wechat/markdown/plain) |

## 使用场景

- "识别这张截图里的文字"
- "分析这个图表的数据"
- "描述这张封面图的视觉元素"
- "这张图片适合什么配文？"
