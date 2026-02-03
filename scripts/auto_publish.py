#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Article Automated Pipeline
Orchestrates: writing -> cover -> formatting -> publishing
"""

import os
import sys
import subprocess
import argparse
import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / ".claude" / "skills"
ARTICLES_DIR = BASE_DIR / "articles"
FORMATTER_DIR = SKILLS_DIR / "wechat-article-formatter"
PUBLISHER_DIR = SKILLS_DIR / "wechat-draft-publisher"
COVER_GEN_DIR = SKILLS_DIR / "wechat-viral-cover"

def run_step(command, cwd=None, description="Step"):
    print(f"\n>>> [{description}] Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=False)
    if result.returncode != 0:
        print(f"!!! Error in {description}")
        return False
    return True

def auto_pipeline(topic, title, author, dry_run=False):
    # 1. Ensure directories exist
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Writing handles by Agent (assuming article.md exists or generated)
    # For this script, we assume the user provides the Markdown file or it's generated
    article_name = topic.replace(" ", "_").lower()[:20]
    md_path = ARTICLES_DIR / f"{article_name}.md"
    
    if not md_path.exists():
        print(f"!!! Article file not found: {md_path}")
        print("Please ensure the Agent has generated the article content first.")
        return

    # 3. Generate Cover
    cover_path = ARTICLES_DIR / "cover.png"
    cover_cmd = [
        sys.executable,
        str(COVER_GEN_DIR / "scripts" / "generate_cover.py"),
        "--title", title,
        "--output", str(cover_path),
        "--api", "local" # Default to local if Gemini not configured
    ]
    if not run_step(cover_cmd, cwd=COVER_GEN_DIR, description="Generating Cover"):
        print("Warning: Cover generation failed, proceeding without it or using fallback.")

    # 4. Format to HTML
    html_path = ARTICLES_DIR / f"{article_name}_formatted.html"
    format_cmd = [
        sys.executable,
        str(FORMATTER_DIR / "scripts" / "markdown_to_html.py"),
        "--input", str(md_path),
        "--theme", "tech", # Adjust based on preference
        "--output", str(html_path)
    ]
    if not run_step(format_cmd, cwd=FORMATTER_DIR, description="Formatting to HTML"):
        return

    # 5. Publish to Drafts
    if dry_run:
        print("\n>>> [Dry Run] Skipping upload to WeChat.")
        print(f"Final Artifacts: \n - {md_path}\n - {html_path}\n - {cover_path}")
        return

    publish_cmd = [
        sys.executable,
        str(PUBLISHER_DIR / "publisher.py"),
        "--title", title,
        "--content", str(html_path),
        "--author", author,
        "--cover", str(cover_path) if cover_path.exists() else ""
    ]
    
    # Filter empty strings from command
    publish_cmd = [c for c in publish_cmd if c]
    
    if not run_step(publish_cmd, cwd=PUBLISHER_DIR, description="Publishing to WeChat Drafts"):
        return

    # 6. Verify
    verify_cmd = [
        sys.executable,
        str(BASE_DIR / "scripts" / "verify_drafts.py")
    ]
    run_step(verify_cmd, cwd=BASE_DIR, description="Verifying Drafts")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-Publish WeChat Article")
    parser.add_argument("--topic", required=True, help="Topic for the article")
    parser.add_argument("--title", required=True, help="Final article title")
    parser.add_argument("--author", default="雲帆AI", help="Author name")
    parser.add_argument("--dry-run", action="store_true", help="Run without uploading")
    
    args = parser.parse_args()
    auto_pipeline(args.topic, args.title, args.author, dry_run=args.dry_run)
