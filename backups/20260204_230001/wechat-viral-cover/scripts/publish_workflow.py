#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号发布工作流 - 完整流程

流程：
1. Markdown 转 HTML（wechat-article-formatter）
2. 智能封面生成（smart_cover_generator: Gemini -> ComfyUI -> 本地）
3. 发布到草稿箱（wechat-draft-publisher）

用法：
python publish_workflow.py --input article.md --title "文章标题" --author "作者"
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 工作流步骤
STEP_MARKDOWN = "markdown"      # Markdown -> HTML
STEP_COVER = "cover"           # 智能封面生成
STEP_PUBLISH = "publish"       # 发布到草稿箱
STEP_ALL = "all"               # 执行全部步骤


def run_markdown_to_html(input_file: str, output_file: str = None, theme: str = "tech") -> bool:
    """执行 Markdown 转 HTML"""
    print("\n" + "=" * 50)
    print("[STEP 1/3] Markdown 转 HTML")
    print("=" * 50)

    md_script = PROJECT_ROOT / ".claude/skills/wechat-article-formatter/scripts/markdown_to_html.py"

    if not md_script.exists():
        print(f"[ERROR] Markdown 转换脚本不存在: {md_script}")
        return False

    cmd = [
        sys.executable, str(md_script),
        "--input", input_file,
        "--theme", theme
    ]

    if output_file:
        cmd.extend(["--output", output_file])

    print(f"执行命令: {' '.join(cmd)}")

    result = os.system(" ".join(cmd))
    if result == 0:
        print("[OK] Markdown 转换成功")
        return True
    else:
        print(f"[ERROR] Markdown 转换失败 (退出码: {result})")
        return False


def run_smart_cover(title: str, output_file: str = "cover.png") -> bool:
    """执行智能封面生成"""
    print("\n" + "=" * 50)
    print("[STEP 2/3] 智能封面生成")
    print("优先级: Gemini -> ComfyUI -> 本地备用")
    print("=" * 50)

    cover_script = PROJECT_ROOT / ".claude/skills/wechat-viral-cover/scripts/smart_cover_generator.py"

    if not cover_script.exists():
        print(f"[ERROR] 封面生成脚本不存在: {cover_script}")
        return False

    cmd = [
        sys.executable, str(cover_script),
        "--title", title,
        "--output", output_file
    ]

    print(f"执行命令: {' '.join(cmd)}")

    result = os.system(" ".join(cmd))
    if result == 0:
        print("[OK] 封面生成成功")
        return True
    else:
        print(f"[ERROR] 封面生成失败 (退出码: {result})")
        return False


def run_publish(title: str, content_file: str, cover_file: str = None, author: str = "冻志强", digest: str = None) -> bool:
    """执行发布到草稿箱"""
    print("\n" + "=" * 50)
    print("[STEP 3/3] 发布到公众号草稿箱")
    print("=" * 50)

    publish_script = PROJECT_ROOT / ".claude/skills/wechat-draft-publisher/publisher.py"

    if not publish_script.exists():
        print(f"[ERROR] 发布脚本不存在: {publish_script}")
        return False

    cmd = [
        sys.executable, str(publish_script),
        "--title", title,
        "--content", content_file,
        "--author", author
    ]

    if cover_file and os.path.exists(cover_file):
        cmd.extend(["--cover", cover_file])

    if digest:
        cmd.extend(["--digest", digest])

    print(f"执行命令: {' '.join(cmd)}")

    result = os.system(" ".join(cmd))
    if result == 0:
        print("[OK] 发布成功")
        return True
    else:
        print(f"[ERROR] 发布失败 (退出码: {result})")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="公众号发布工作流 - 完整流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 执行全部流程
  python publish_workflow.py --input article.md --title "我的文章标题"

  # 仅生成 HTML
  python publish_workflow.py --input article.md --step markdown

  # 仅生成封面
  python publish_workflow.py --title "我的文章标题" --step cover

  # 仅发布（需要已存在 article_formatted.html 和 cover.png）
  python publish_workflow.py --step publish --title "标题"
        """
    )

    parser.add_argument("--input", "-i", help="输入 Markdown 文件路径")
    parser.add_argument("--title", "-t", required=True, help="文章标题")
    parser.add_argument("--author", default="冻志强", help="作者名称")
    parser.add_argument("--digest", "-d", help="文章摘要")
    parser.add_argument("--step", choices=[STEP_MARKDOWN, STEP_COVER, STEP_PUBLISH, STEP_ALL],
                       default=STEP_ALL, help="执行步骤 (默认: all)")
    parser.add_argument("--theme", choices=["tech", "minimal", "business"],
                       default="tech", help="主题风格 (默认: tech)")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  公众号发布工作流")
    print("=" * 60)
    print(f"  标题: {args.title}")
    print(f"  作者: {args.author}")
    print(f"  步骤: {args.step}")
    print(f"  主题: {args.theme}")
    print("=" * 60)

    # 根据步骤执行
    success = True

    if args.step in [STEP_MARKDOWN, STEP_ALL]:
        input_file = args.input or f"{args.title[:20]}.md"

        if not os.path.exists(input_file):
            print(f"[ERROR] 输入文件不存在: {input_file}")
            success = False
        else:
            output_html = f"{Path(input_file).stem}_formatted.html"
            if not run_markdown_to_html(input_file, output_html, args.theme):
                success = False

    if args.step in [STEP_COVER, STEP_ALL]:
        cover_file = "cover.png"
        if not run_smart_cover(args.title, cover_file):
            # 封面失败不中断流程，使用无封面模式
            print("[WARN] 封面生成失败，将使用无封面模式发布")

    if args.step in [STEP_PUBLISH, STEP_ALL]:
        # 查找 HTML 文件
        if args.input:
            html_file = f"{Path(args.input).stem}_formatted.html"
        else:
            html_file = f"{args.title[:20]}_formatted.html"

        if not os.path.exists(html_file):
            print(f"[ERROR] HTML 文件不存在: {html_file}")
            print("请先执行 --step markdown 生成 HTML")
            success = False
        else:
            cover_file = "cover.png" if os.path.exists("cover.png") else None
            if not run_publish(args.title, html_file, cover_file, args.author, args.digest):
                success = False

    # 总结
    print("\n" + "=" * 60)
    if success:
        print("  [SUCCESS] 工作流执行完成!")
        print("  请登录微信公众平台查看草稿")
    else:
        print("  [FAILED] 工作流执行失败，请检查上方错误信息")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
