#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爆款封面生成器
基于雲帆AI的爆款封面法则（视觉冲突 + 情绪锚点）
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径 - wechat_article_skills 是项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 尝试导入图片生成模块
try:
    from .claude.skills.wechat_product_manager_writer.scripts.generate_image import generate_image
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# 爆款封面提示词模板库
COVER_TEMPLATES = {
    "fear": {
        # 宏观恐惧类 - 适用于危机、崩盘、AI替代、大国博弈
        "name": "宏观恐惧",
        "subject": "A tiny silhouette of a person in a suit, standing on the edge of a crumbling cliff.",
        "environment": "In front of them, a massive, overwhelming force crashing down - [VISUAL_ELEMENT] made of dark ominous materials.",
        "mood": "Overwhelming pressure, despair, sense of impending doom.",
        "lighting": "Dramatic Rim Lighting, dark background with blood red highlights, volumetric fog.",
        "composition": "Extreme Low Angle looking up, Rule of Thirds, epic scale.",
        "style": "Hyper-realistic 3D render, Unreal Engine 5, 8k resolution, cinematic depth of field.",
        "visual_elements": {
            "金融危机": "stock market crash, red candlestick charts, falling coins",
            "AI替代": "glitching human faces being replaced by robotic skulls",
            "楼市崩盘": "crumbling concrete buildings, falling concrete debris",
            "大国博弈": "colliding tectonic plates, massive military vehicles",
            "默认": "tsunami of red numbers and broken chains",
        }
    },
    "twist": {
        # 认知颠覆类 - 适用于揭秘、底层逻辑、黑科技
        "name": "认知颠覆",
        "subject": "A realistic human head or iconic symbol, but half of it is peeled away or sliced open.",
        "environment": "Inside the sliced section, it reveals [VISUAL_ELEMENT] - unexpected, surreal, mind-bending.",
        "mood": "Shocking revelation, surreal mystery, the moment of truth.",
        "lighting": "Volumetric Spotlight on the open section, deep shadows elsewhere, chiaroscuro.",
        "composition": "Center composition, symmetrical but broken, unsettling balance.",
        "style": "Surrealism in the style of Salvador Dali, macro photography, intricate details, hyper-detailed.",
        "visual_elements": {
            "揭秘": "ancient clockwork gears and mechanisms, dusty secrets",
            "底层逻辑": "glowing data streams, quantum particles, fractal patterns",
            "黑科技": "alien technology, glowing energy cores, quantum fragments",
            "真相": "a blinding white light, cosmic void, infinite mirror",
            "默认": "mysterious glowing artifacts, surreal landscape",
        }
    },
    "success": {
        # 普通人逆袭类 - 适用于副业、搞钱、阶级跨越
        "name": "逆袭成功",
        "subject": "Rough, dirty hands holding a glowing, pristine [OBJECT] - extreme contrast.",
        "environment": "Split background: Left side is grey, rainy urban slum; Right side is golden, futuristic city of wealth.",
        "mood": "Hope, yearning, the moment of breakthrough, sudden wealth.",
        "lighting": "Golden Hour sunlight hitting the object, extreme contrast between warm gold and cool grey.",
        "composition": "Split screen effect implied, extreme close-up on the hands, hands as the bridge.",
        "style": "Cinematic Realism, high texture details (dirt under nails vs polished gold), movie poster quality.",
        "visual_elements": {
            "搞钱": "golden Bitcoin, glowing coins, money raining down",
            "副业": "laptop showing dollar signs, multiple screens with charts",
            "阶级跨越": "elevator going up, stairs transforming into gold",
            "逆袭": "rising phoenix, breaking through concrete ceiling",
            "默认": "glowing golden key, treasure chest, winning lottery ticket",
        },
        "objects": {
            "搞钱": "golden Bitcoin",
            "副业": "laptop with dollar signs",
            "逆袭": "golden trophy",
            "默认": "shining golden key",
        }
    },
    "bio": {
        # 历史/人物传记类 - 适用于大人物、历史
        "name": "人物传记",
        "subject": "Extreme hyper-detailed portrait of [NAME], staring directly into the camera lens with piercing eyes.",
        "environment": "Pitch black background fading into smoke and dust, ominous and historic.",
        "mood": "Intense stare, eyes full of wisdom, regret, power and determination.",
        "lighting": "Rembrandt Lighting - dramatic triangle of light on cheek, heavy shadows, cinematic.",
        "composition": "Extreme Close-up focusing on eyes and nose, Rule of Eye.",
        "style": "Oil painting texture mixed with 8k photography, gritty, sharp focus, textured skin.",
        "objects": {
            "马斯克": "Elon Musk",
            "乔布斯": "Steve Jobs",
            "巴菲特": "Warren Buffett",
            "默认": "mysterious powerful figure",
        }
    },
    "tech": {
        # 科技产品类 - 适用于工具评测、软件推荐
        "name": "科技产品",
        "subject": "[PRODUCT] in dramatic lighting, glowing with ethereal blue light, floating in cyber space.",
        "environment": "Dark tech laboratory background, holographic interfaces, data streams flowing.",
        "mood": "Innovation, power, future tech, sleek and powerful.",
        "lighting": "Cyberpunk neon blue and purple rim lighting, volumetric glow, cinematic.",
        "composition": "Center composition, slight Dutch angle, product as hero.",
        "style": "Product photography meets sci-fi, 8k, hyper-realistic, sleek.",
        "visual_elements": {
            "AI工具": "AI brain circuits, neural networks, glowing synapses",
            "软件": "floating UI elements, holographic interface",
            "硬件": "sleek device details, LED indicators, premium materials",
            "默认": "generic tech product in epic lighting",
        }
    },
    "story": {
        # 故事类 - 适用于个人经历、情感共鸣
        "name": "故事共鸣",
        "subject": "A single human figure in silhouette, standing against a massive [VISUAL] that represents their struggle or triumph.",
        "environment": "Dramatic environment that tells the story - [ENVIRONMENT].",
        "mood": "Emotional resonance, journey, transformation, the human spirit.",
        "lighting": "God ray sunlight from above, dramatic shadows, emotional and cinematic.",
        "composition": "Rule of Thirds, figure as small but significant, environment overwhelming.",
        "style": "Cinematic still, movie poster quality, emotional storytelling.",
        "visual_elements": {
            "失败": "fallen giants, destroyed dreams, dark stormy sky",
            "成功": "golden sunrise breaking through clouds, mountain peak",
            "转变": "doorway to new world, bridge between worlds",
            "默认": "dramatic clouds, symbolic landscape",
        }
    }
}

# 中英文映射
TOPIC_MAPPING = {
    # 恐惧类
    "危机": "fear", "金融危机": "fear", "崩盘": "fear", "失业": "fear",
    "AI替代": "fear", "裁员": "fear", "经济": "fear", "战争": "fear",
    # 颠覆类
    "揭秘": "twist", "真相": "twist", "底层逻辑": "twist", "黑科技": "twist",
    "秘密": "twist", "内幕": "twist", "真相": "twist", "不知道": "twist",
    # 逆袭类
    "搞钱": "success", "赚钱": "success", "副业": "success", "逆袭": "success",
    "暴富": "success", "财富": "success", "收入": "success", "月入": "success",
    # 人物类
    "马斯克": "bio", "乔布斯": "bio", "巴菲特": "bio", "人物": "bio",
    "传记": "bio", "历史": "bio", "伟人": "bio",
    # 科技类
    "AI": "tech", "工具": "tech", "软件": "tech", "产品": "tech",
    "评测": "tech", "推荐": "tech", "ChatGPT": "tech", "Claude": "tech",
    # 故事类
    "故事": "story", "经历": "story", "我是如何": "story", "心得": "story",
    "感悟": "story", "分享": "story", "经验": "story",
}


def detect_type(title: str) -> str:
    """根据标题自动检测封面类型"""
    title_lower = title.lower()

    for keyword, type_name in TOPIC_MAPPING.items():
        if keyword in title_lower:
            return type_name

    # 默认返回科技类（最常见）
    return "tech"


def build_prompt(template: dict, title: str, type_name: str) -> str:
    """构建完整的提示词"""
    prompt_parts = []

    # 主体
    subject = template["subject"]
    # 根据标题替换特定元素
    if type_name == "success":
        obj_template = template.get("objects", {})
        for key, obj in obj_template.items():
            if key in title:
                subject = subject.replace("[OBJECT]", obj)
                break
        else:
            subject = subject.replace("[OBJECT]", obj_template.get("默认", "golden key"))
    elif type_name == "bio":
        name_template = template.get("objects", {})
        for key, name in name_template.items():
            if key in title:
                subject = subject.replace("[NAME]", name)
                break
        else:
            subject = subject.replace("[NAME]", "mysterious powerful figure")

    prompt_parts.append(subject)

    # 环境
    environment = template["environment"]
    if "[VISUAL]" in environment:
        vis_template = template.get("visual_elements", {})
        matched = False
        for key, visual in vis_template.items():
            if key in title:
                environment = environment.replace("[VISUAL]", visual)
                matched = True
                break
        else:
            environment = environment.replace("[VISUAL]", vis_template.get("默认", "dramatic clouds"))
    elif "[VISUAL_ELEMENT]" in environment:
        vis_template = template.get("visual_elements", {})
        matched = False
        for key, visual in vis_template.items():
            if key in title:
                environment = environment.replace("[VISUAL_ELEMENT]", visual)
                matched = True
                break
        else:
            environment = environment.replace("[VISUAL_ELEMENT]", vis_template.get("默认", "ominous shadows"))

    prompt_parts.append(environment)

    # 情绪
    prompt_parts.append(template["mood"])

    # 光影
    prompt_parts.append(template["lighting"])

    # 构图
    prompt_parts.append(template["composition"])

    # 风格
    prompt_parts.append(template["style"])

    return ", ".join(prompt_parts)


def generate_cover_image(prompt: str, output_path: str, api: str = "comfyui") -> bool:
    """生成封面图片"""
    # 优先使用 ComfyUI（本地 AI 生成，效果最好）
    if api == "comfyui":
        try:
            # 使用现有的 ComfyUI 客户端
            workflow_file = Path("C:/Users/52648/Documents/GitHub/wechat_article_skills/.claude/skills/comfyui-image-generator/assets/default_workflow.json")

            if not workflow_file.exists():
                raise FileNotFoundError(f"ComfyUI 工作流不存在: {workflow_file}")

            # 加载工作流
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow = json.load(f)

            # 修改提示词 (节点 67)
            if "67" in workflow:
                workflow["67"]["inputs"]["text"] = prompt

            # 调整尺寸为公众号封面比例 3.35:1 (900x268)
            if "68" in workflow:
                workflow["68"]["inputs"]["width"] = 900
                workflow["68"]["inputs"]["height"] = 268

            # 修改输出文件名
            if "9" in workflow:
                workflow["9"]["inputs"]["filename_prefix"] = Path(output_path).stem

            # 执行工作流 - 从 comfyui-image-generator 导入
            comfyui_client_path = PROJECT_ROOT / ".claude/skills/comfyui-image-generator/scripts/comfyui_client.py"
            import importlib.util
            spec = importlib.util.spec_from_file_location("comfyui_client", str(comfyui_client_path))
            comfyui_client = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(comfyui_client)
            ComfyUIClient = comfyui_client.ComfyUIClient
            client = ComfyUIClient("http://127.0.0.1:8188")

            print("提交到 ComfyUI...")
            result = client.queue_prompt(workflow)
            prompt_id = result.get("prompt_id", "unknown")
            print(f"任务已提交: {prompt_id}")

            print("生成中...")
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
                        print(f"[OK] 封面生成成功: {output_path}")
                        return True

            print("[FAIL] 未找到生成的图像")
            return False

        except ImportError as e:
            print(f"[WARN] ComfyUI 客户端不可用: {e}")
            return False
        except Exception as e:
            print(f"[WARN] ComfyUI 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    if api == "gemini" and GEMINI_AVAILABLE:
        try:
            result = generate_image(
                prompt=prompt,
                api="gemini",
                output=output_path
            )
            return result is not None
        except Exception as e:
            print(f"[WARN] Gemini 生成失败: {e}")
            return False

    # 如果 Gemini/ComfyUI 不可用，使用本地 Pillow
    return generate_local_cover(prompt, output_path)


def generate_local_cover(prompt: str, output_path: str) -> bool:
    """使用本地 Pillow 生成备用封面"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random

        # 创建渐变背景
        width, height = 900, 500
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # 生成科技感渐变背景
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

        # 添加装饰性元素
        draw.ellipse((650, -100, 850, 150), fill=(88, 86, 214, 180))
        draw.ellipse ((-50, 300, 250, 550), fill=(0, 122, 255, 150))

        # 添加文字
        title_text = "爆款封面"
        try:
            font = ImageFont.truetype("msyh.ttc", 60)
            title_font = ImageFont.truetype("msyh.ttc", 40)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()

        # 标题
        draw.text((50, 180), "爆款封面", font=title_font, fill=(255, 255, 255))
        draw.text((50, 250), "生成成功", font=title_font, fill=(88, 86, 214))

        # 保存
        img.save(output_path, 'PNG')
        print(f"[OK] 本地封面生成成功: {output_path}")
        return True

    except ImportError:
        print("[ERROR] Pillow 不可用，无法生成封面")
        return False
    except Exception as e:
        print(f"[ERROR] 本地封面生成失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="爆款封面生成器")
    parser.add_argument("--title", "-t", required=True, help="文章标题")
    parser.add_argument("--type", choices=["fear", "twist", "success", "bio", "tech", "story"],
                       help="封面类型 (自动检测)")
    parser.add_argument("--output", "-o", default="cover.png", help="输出文件路径")
    parser.add_argument("--api", choices=["comfyui", "gemini", "local"], default="comfyui", help="使用的 API (comfyui/gemini/local)")

    args = parser.parse_args()

    # 自动检测类型
    cover_type = args.type or detect_type(args.title)

    if cover_type not in COVER_TEMPLATES:
        cover_type = "tech"

    template = COVER_TEMPLATES[cover_type]
    print(f"=== 爆款封面生成 ===")
    print(f"标题: {args.title}")
    print(f"类型: {template['name']}")

    # 构建提示词
    prompt = build_prompt(template, args.title, cover_type)
    print(f"\n提示词:\n{prompt}\n")

    # 生成图片
    print("正在生成封面...")
    success = generate_cover_image(prompt, args.output, args.api)

    if success:
        print(f"\n[OK] 封面生成成功: {args.output}")
    else:
        print(f"\n[WARN] 使用备用方案...")
        success = generate_local_cover(prompt, args.output)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
