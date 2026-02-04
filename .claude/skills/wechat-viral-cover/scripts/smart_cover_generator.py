#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能封面生成器 - 自动切换 AI 服务

优先级：
1. Gemini API（云端 AI）
2. ComfyUI（本地 AI）
3. 本地 Pillow（备用）

用法：
python smart_cover_generator.py --title "文章标题" --output cover.png
"""

import argparse
import sys
import json
import os
from pathlib import Path

# 添加项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_gemini_available():
    """检查 Gemini API 是否可用"""
    try:
        from claude.skills.wechat_product_manager_writer.scripts.generate_image import generate_image
        return True
    except ImportError:
        return False


def check_comfyui_available(server_url: str = "http://127.0.0.1:8188") -> tuple:
    """检查 ComfyUI 是否可用，返回 (可用, 错误信息)"""
    try:
        import ssl
        from urllib.request import Request, urlopen
        from urllib.error import URLError, HTTPError

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = Request(f"{server_url}/api/system_stats", method='GET')
        with urlopen(req, timeout=10, context=ctx) as resp:
            return True, None
    except ImportError as e:
        return False, f"导入错误: {e}"
    except Exception as e:
        return False, str(e)


def generate_with_gemini(prompt: str, output_path: str) -> bool:
    """使用 Gemini API 生成封面"""
    try:
        from claude.skills.wechat_product_manager_writer.scripts.generate_image import generate_image
        print("[INFO] 正在使用 Gemini API 生成封面...")
        result = generate_image(prompt=prompt, api="gemini", output=output_path)
        if result is not None:
            print(f"[OK] Gemini 生成成功: {output_path}")
            return True
        print("[WARN] Gemini 返回空结果")
        return False
    except Exception as e:
        print(f"[WARN] Gemini 生成失败: {e}")
        return False


def generate_with_comfyui(prompt: str, output_path: str, server_url: str = "http://127.0.0.1:8188") -> bool:
    """使用 ComfyUI 生成封面"""
    try:
        workflow_file = Path(__file__).parent / "assets" / "cover_workflow.json"

        if not workflow_file.exists():
            # 使用默认工作流
            workflow_file = Path(PROJECT_ROOT) / ".claude/skills/comfyui-image-generator/assets/default_workflow.json"

        if not workflow_file.exists():
            print(f"[WARN] ComfyUI 工作流文件不存在: {workflow_file}")
            return False

        # 加载工作流
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)

        # 修改提示词
        for node_id, node in workflow.items():
            if isinstance(node, dict) and node.get("class_type") in ["CLIPTextEncode", "CLIPTextEncodeSDXL", "Text Prompt"]:
                if "inputs" in node and "text" in node["inputs"]:
                    node["inputs"]["text"] = prompt
                    print(f"[INFO] 已更新节点 {node_id} 的提示词")

        # 调整尺寸为 900x500（公众号封面）
        for node_id, node in workflow.items():
            if isinstance(node, dict) and "class_type" in node:
                if "EmptyLatentImage" in node["class_type"] or "分辨率" in str(node):
                    if "inputs" in node:
                        if "width" in node["inputs"]:
                            node["inputs"]["width"] = 900
                        if "height" in node["inputs"]:
                            node["inputs"]["height"] = 500

        # 修改输出文件名
        for node_id, node in workflow.items():
            if isinstance(node, dict) and "SaveImage" in node.get("class_type", ""):
                if "inputs" in node and "filename_prefix" in node["inputs"]:
                    node["inputs"]["filename_prefix"] = Path(output_path).stem

        # 调用 ComfyUI
        print("[INFO] 正在使用 ComfyUI 生成封面...")

        # 动态导入 ComfyUI 客户端
        comfyui_script = Path(PROJECT_ROOT) / ".claude/skills/comfyui-image-generator/scripts/comfyui_client.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("comfyui_client", str(comfyui_script))
        comfyui_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(comfyui_module)

        client = comfyui_module.ComfyUIClient(server_url)
        result = client.queue_prompt({"prompt": workflow, "client_id": client.client_id})
        prompt_id = result.get("prompt_id", "unknown")
        print(f"[INFO] 任务已提交: {prompt_id}")

        # 等待完成
        print("[INFO] ComfyUI 生成中...")
        outputs = client.wait_for_completion(timeout=300)

        # 保存图像
        for node_id, output_data in outputs.items():
            if isinstance(output_data, dict) and "images" in output_data:
                for img in output_data["images"]:
                    filename = img["filename"]
                    subfolder = img.get("subfolder", "")
                    image_data = client.get_image(filename, subfolder)

                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    print(f"[OK] ComfyUI 生成成功: {output_path}")
                    return True

        print("[WARN] 未找到 ComfyUI 生成的图像")
        return False

    except Exception as e:
        print(f"[WARN] ComfyUI 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_local_cover(title: str, output_path: str) -> bool:
    """使用本地 Pillow 生成备用封面"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        width, height = 900, 500
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # 渐变背景
        colors = [
            (26, 26, 29),    # 深灰
            (88, 86, 214),   # 紫色
            (0, 122, 255),   # 蓝色
        ]

        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio + (colors[2][0] - colors[1][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio + (colors[2][1] - colors[1][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio + (colors[2][2] - colors[1][2]) * ratio)
            for x in range(width):
                img.putpixel((x, y), (r, g, b))

        # 装饰
        draw.ellipse((650, -100, 850, 150), fill=(88, 86, 214, 180))
        draw.ellipse((-50, 300, 250, 550), fill=(0, 122, 255, 150))

        # 标题文字
        try:
            font = ImageFont.truetype("msyh.ttc", 40)
        except:
            font = ImageFont.load_default()

        # 标题（截断）
        display_title = title[:20] + "..." if len(title) > 20 else title
        draw.text((50, 200), display_title, font=font, fill=(255, 255, 255))
        draw.text((50, 260), "备用封面", font=font, fill=(88, 86, 214))

        img.save(output_path, 'PNG')
        print(f"[OK] 本地备用封面生成成功: {output_path}")
        return True

    except ImportError:
        print("[ERROR] Pillow 不可用，无法生成备用封面")
        return False
    except Exception as e:
        print(f"[ERROR] 本地封面生成失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="智能封面生成器 - 自动切换 AI 服务")
    parser.add_argument("--title", "-t", required=True, help="文章标题")
    parser.add_argument("--output", "-o", default="cover.png", help="输出文件路径")
    parser.add_argument("--server-url", "-s", default="http://127.0.0.1:8188", help="ComfyUI 服务器地址")

    args = parser.parse_args()

    print("=" * 50)
    print("智能封面生成器")
    print("优先级: Gemini → ComfyUI → 本地备用")
    print("=" * 50)
    print(f"标题: {args.title}")
    print(f"输出: {args.output}")
    print("-" * 50)

    # 1. 优先尝试 Gemini
    print("\n[STEP 1/3] 检查 Gemini API...")
    if check_gemini_available():
        print("[OK] Gemini 可用")
        # 构建提示词（复用 wechat-viral-cover 的模板）
        from .generate_cover import build_prompt, detect_type, COVER_TEMPLATES

        cover_type = detect_type(args.title)
        template = COVER_TEMPLATES.get(cover_type, COVER_TEMPLATES["tech"])
        prompt = build_prompt(template, args.title, cover_type)

        print(f"\n提示词:\n{prompt[:200]}...\n")

        if generate_with_gemini(prompt, args.output):
            print("\n[SUCCESS] 封面生成完成 (Gemini)")
            return 0
    else:
        print("[WARN] Gemini 不可用")

    # 2. 尝试 ComfyUI
    print("\n[STEP 2/3] 检查 ComfyUI...")
    comfy_available, comfy_error = check_comfyui_available(args.server_url)
    if comfy_available:
        print("[OK] ComfyUI 可用")

        # 构建提示词
        from .generate_cover import build_prompt, detect_type, COVER_TEMPLATES

        cover_type = detect_type(args.title)
        template = COVER_TEMPLATES.get(cover_type, COVER_TEMPLATES["tech"])
        prompt = build_prompt(template, args.title, cover_type)

        if generate_with_comfyui(prompt, args.output, args.server_url):
            print("\n[SUCCESS] 封面生成完成 (ComfyUI)")
            return 0
    else:
        print(f"[WARN] ComfyUI 不可用: {comfy_error}")

    # 3. 使用本地备用
    print("\n[STEP 3/3] 使用本地备用封面...")
    if generate_local_cover(args.title, args.output):
        print("\n[INFO] 使用本地备用封面完成")
        return 0

    print("\n[FAILED] 所有方案均失败")
    return 1


if __name__ == "__main__":
    sys.exit(main())
