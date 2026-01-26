from PIL import Image, ImageDraw, ImageFont
import textwrap
import argparse
import os
import random

def create_cover(title, subtitle, output_path, theme='blue'):
    # 微信封面最佳比例 2.35:1 (900x383)
    width = 900
    height = 383
    
    # 配色方案
    themes = {
        'blue': {'bg': (26, 31, 92), 'text': (255, 255, 255), 'accent': (0, 255, 255)}, # 科技蓝
        'green': {'bg': (16, 185, 129), 'text': (255, 255, 255), 'accent': (255, 230, 0)}, # 效率绿
        'dark': {'bg': (30, 30, 30), 'text': (255, 255, 255), 'accent': (255, 100, 100)}, # 商务黑
    }
    
    colors = themes.get(theme, themes['blue'])
    
    # 创建背景
    img = Image.new('RGB', (width, height), color=colors['bg'])
    draw = ImageDraw.Draw(img)
    
    # 添加一些简单的几何装饰
    for _ in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(20, 100)
        draw.ellipse([x-r, y-r, x+r, y+r], outline=colors['accent'], width=2)

    # 尝试加载中文字体，如果失败则使用默认
    try:
        # 尝试 Windows 常见字体
        font_path = "C:\\Windows\\Fonts\\msyh.ttc" # 微软雅黑
        if not os.path.exists(font_path):
             font_path = "C:\\Windows\\Fonts\\simhei.ttf" # 黑体
        
        title_font = ImageFont.truetype(font_path, 60)
        subtitle_font = ImageFont.truetype(font_path, 36)
    except:
        print("Warning: Chinese font not found, using default.")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # 绘制标题 (自动换行)
    margin = 50
    para = textwrap.wrap(title, width=15) # 估算每行字数
    
    current_h = 80
    for line in para:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width - w) / 2, current_h), line, font=title_font, fill=colors['text'])
        current_h += h + 20
    
    # 绘制副标题
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        w = bbox[2] - bbox[0]
        draw.text(((width - w) / 2, current_h + 20), subtitle, font=subtitle_font, fill=colors['accent'])

    # 保存
    img.save(output_path)
    print(f"Cover generated: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--theme", default="blue")
    args = parser.parse_args()
    
    create_cover(args.title, args.subtitle, args.output, args.theme)
