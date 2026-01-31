from PIL import Image, ImageDraw, ImageFont
import textwrap
import argparse
import os
import random

def create_cover(title, subtitle, output_path, theme='blue', width=900, height=383):
    themes = {
        'blue': {'bg': (26, 31, 92), 'text': (255, 255, 255), 'accent': (0, 255, 255)},
        'green': {'bg': (16, 185, 129), 'text': (255, 255, 255), 'accent': (255, 230, 0)},
        'dark': {'bg': (30, 30, 30), 'text': (255, 255, 255), 'accent': (255, 100, 100)},
    }
    colors = themes.get(theme, themes['blue'])

    img = Image.new('RGB', (width, height), color=colors['bg'])
    draw = ImageDraw.Draw(img)

    for _ in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(20, min(width, height) // 9)
        draw.ellipse([x-r, y-r, x+r, y+r], outline=colors['accent'], width=2)

    try:
        font_path = "C:\\Windows\\Fonts\\msyh.ttc"
        if not os.path.exists(font_path):
            font_path = "C:\\Windows\\Fonts\\simhei.ttf"
        base_size = max(40, min(width, height) // 15)
        title_font = ImageFont.truetype(font_path, base_size + 20)
        subtitle_font = ImageFont.truetype(font_path, base_size)
    except:
        print("Warning: Chinese font not found, using default.")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    margin = max(40, min(width, height) // 20)
    para = textwrap.wrap(title, width=15)

    current_h = margin + 30
    for line in para:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width - w) / 2, current_h), line, font=title_font, fill=colors['text'])
        current_h += h + 20

    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        w = bbox[2] - bbox[0]
        draw.text(((width - w) / 2, current_h + 20), subtitle, font=subtitle_font, fill=colors['accent'])

    img.save(output_path)
    print(f"Cover generated: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--theme", default="blue")
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=383)
    args = parser.parse_args()
    create_cover(args.title, args.subtitle, args.output, args.theme, args.width, args.height)
