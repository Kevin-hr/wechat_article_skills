#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像识别器
支持多模型：GPT-4 Vision、Gemini、Claude Vision
"""

import argparse
import base64
import os
import sys
from pathlib import Path
from typing import Optional

# 尝试导入各模型 SDK
GPT_AVAILABLE = False
GEMINI_AVAILABLE = False
CLAUDE_AVAILABLE = False
DEEPSEEK_AVAILABLE = False

try:
    import openai
    GPT_AVAILABLE = True
except ImportError:
    pass

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    pass

try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    pass


def encode_image(image_path: str) -> str:
    """将图片编码为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def recognize_with_gpt(image_path: str, task: str = "describe") -> str:
    """使用 GPT-4 Vision 识别"""
    if not GPT_AVAILABLE:
        raise ImportError("请安装 openai: pip install openai")

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # 任务提示词
    prompts = {
        "describe": "请详细描述这张图片的内容，包括主体、环境、颜色、氛围等。",
        "ocr": "请提取这张图片中的所有文字，保持原格式。",
        "analyze": "请分析这张图片（可能是图表或数据图），提取关键数据点和结论。",
        "wechat": "请用适合微信公众号的风格描述这张图片，用于配图文案。"
    }

    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompts.get(task, prompts["describe"])},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content


def recognize_with_gemini(image_path: str, task: str = "describe") -> str:
    """使用 Gemini 识别"""
    if not GEMINI_AVAILABLE:
        raise ImportError("请安装 google-genai: pip install google-genai")

    from google import genai

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompts = {
        "describe": "Describe this image in detail, including subject, environment, colors, and atmosphere.",
        "ocr": "Extract all text from this image, keeping the original format.",
        "analyze": "Analyze this image (possibly a chart or data graph) and extract key data points and conclusions.",
        "wechat": "Describe this image in a style suitable for WeChat public account, for use with article captions."
    }

    with open(image_path, "rb") as f:
        image_data = f.read()

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            prompts.get(task, prompts["describe"]),
            {"mime_type": "image/png", "data": image_data}
        ]
    )

    return response.text


def recognize_with_claude(image_path: str, task: str = "describe") -> str:
    """使用 Claude Vision 识别"""
    if not CLAUDE_AVAILABLE:
        raise ImportError("请安装 anthropic: pip install anthropic")

    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompts = {
        "describe": "请详细描述这张图片的内容，包括主体、环境、颜色、氛围等。",
        "ocr": "请提取这张图片中的所有文字，保持原格式。",
        "analyze": "请分析这张图片（可能是图表或数据图），提取关键数据点和结论。",
        "wechat": "请用适合微信公众号的风格描述这张图片，用于配图文案。"
    }

    base64_image = encode_image(image_path)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompts.get(task, prompts["describe"])},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    }
                ]
            }
        ]
    )

    return response.content[0].text


def recognize_with_deepseek(image_path: str, task: str = "describe") -> str:
    """使用 DeepSeek Vision 识别"""
    if not GPT_AVAILABLE:
        raise ImportError("请安装 openai: pip install openai")

    # DeepSeek API 兼容 OpenAI 格式
    client = openai.OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    prompts = {
        "describe": "请详细描述这张图片的内容，包括主体、环境、颜色、氛围等。",
        "ocr": "请提取这张图片中的所有文字，保持原格式。",
        "analyze": "请分析这张图片（可能是图表或数据图），提取关键数据点和结论。",
        "wechat": "请用适合微信公众号的风格描述这张图片，用于配图文案。"
    }

    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="deepseek-chat",  # DeepSeek Vision 模型
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompts.get(task, prompts["describe"])},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="图像识别器")
    parser.add_argument("--input", "-i", required=True, help="输入图片路径")
    parser.add_argument("--model", "-m", choices=["gpt", "gemini", "claude", "deepseek"], default="deepseek",
                        help="使用的模型 (默认: deepseek)")
    parser.add_argument("--task", "-t", choices=["describe", "ocr", "analyze", "wechat"],
                        default="describe", help="任务类型")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    # 检查文件
    image_path = Path(args.input)
    if not image_path.exists():
        print(f"[错误] 图片不存在: {image_path}")
        return 1

    # 选择模型
    model_func = None
    if args.model == "deepseek":
        if not GPT_AVAILABLE:
            print("[错误] OpenAI SDK 不可用，请安装 openai")
            return 1
        model_func = recognize_with_deepseek
    elif args.model == "gpt":
        if not GPT_AVAILABLE:
            print("[错误] GPT-4 Vision 不可用，请安装 openai")
            return 1
        model_func = recognize_with_gpt
    elif args.model == "gemini":
        if not GEMINI_AVAILABLE:
            print("[错误] Gemini 不可用，请安装 google-genai")
            return 1
        model_func = recognize_with_gemini
    elif args.model == "claude":
        if not CLAUDE_AVAILABLE:
            print("[错误] Claude Vision 不可用，请安装 anthropic")
            return 1
        model_func = recognize_with_claude

    # 执行识别
    print(f"[INFO] 使用 {args.model} 识别图片...")
    try:
        result = model_func(str(image_path), args.task)

        # 输出
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"[OK] 结果已保存: {args.output}")
        else:
            print("\n" + "=" * 50)
            print(result)
            print("=" * 50)

        return 0
    except Exception as e:
        print(f"[错误] 识别失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
