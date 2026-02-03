"""
用户偏好记忆模块

提供用户写作偏好的存储、读取和更新功能。
存储位置: ~/.wechat-writer/preferences.json
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 偏好存储路径
PREFERENCES_DIR = Path(os.path.expanduser("~/.wechat-writer"))
PREFERENCES_FILE = PREFERENCES_DIR / "preferences.json"

# 默认偏好模板
DEFAULT_PREFERENCES = {
    "version": "1.0",
    "last_updated": None,
    "user_profile": {
        "default_author": "雲帆AI",
        "language": "zh-CN",
    },
    "writing_style": {
        "preferred_style": "tech",  # tech / minimal / business
        "first_person": True,
        "include_cover_image": True,
        "include_structure_image": False,
        "word_count_range": [2000, 3500],
        "prose_first": True,
    },
    "cover_preferences": {
        "preferred_theme": "blue",  # blue / green / dark / purple
        "default_ai_api": "gemini",
        "fallback_to_local": True,
        "aspect_ratio": "2.35:1",
    },
    "theme_preferences": {
        "tech": {
            "primary_color": "#1a1f5c",
            "accent_color": "#7c3aed",
        },
        "minimal": {
            "primary_color": "#1a1a1a",
            "accent_color": "#ffffff",
        },
        "business": {
            "primary_color": "#1e3a8a",
            "accent_color": "#fbbf24",
        },
    },
    "publishing": {
        "default_digest_length": 120,
        "auto_optimize_html": True,
        "auto_verify_publish": True,
    },
    "history_summary": {
        "total_articles": 0,
        "last_topic": None,
        "last_topic_category": None,
        "common_topics": {},  # {topic: count}
        "common_categories": {},  # {category: count}
    },
}


def ensure_storage_dir():
    """确保存储目录存在"""
    PREFERENCES_DIR.mkdir(parents=True, exist_ok=True)


def load_preferences() -> Dict[str, Any]:
    """加载用户偏好"""
    ensure_storage_dir()
    if PREFERENCES_FILE.exists():
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 合并默认偏好（处理新增字段）
                return merge_preferences(data, DEFAULT_PREFERENCES.copy())
        except (json.JSONDecodeError, IOError):
            return DEFAULT_PREFERENCES.copy()
    return DEFAULT_PREFERENCES.copy()


def save_preferences(prefs: Dict[str, Any]) -> None:
    """保存用户偏好"""
    ensure_storage_dir()
    prefs["last_updated"] = datetime.now().isoformat()
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def merge_preferences(user: Dict, default: Dict) -> Dict:
    """合并用户偏好与默认偏好"""
    for key, value in default.items():
        if key not in user:
            user[key] = value
        elif isinstance(value, dict) and isinstance(user.get(key), dict):
            merge_preferences(user[key], value)
    return user


def get(key: str, default=None):
    """获取偏好值"""
    prefs = load_preferences()
    keys = key.split(".")
    value = prefs
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default
    return value if value is not None else default


def set_value(key: str, value: Any) -> None:
    """设置偏好值"""
    prefs = load_preferences()
    keys = key.split(".")
    current = prefs
    for k in keys[:-1]:
        current = current.setdefault(k, {})
    current[keys[-1]] = value
    save_preferences(prefs)


def update_writing_feedback(
    style: Optional[str] = None,
    word_count: Optional[int] = None,
    category: Optional[str] = None,
) -> None:
    """根据用户反馈更新偏好"""
    prefs = load_preferences()

    if style:
        prefs["writing_style"]["preferred_style"] = style

    if word_count:
        # 调整字数范围
        current_min, current_max = prefs["writing_style"]["word_count_range"]
        if word_count < current_min * 0.8:
            prefs["writing_style"]["word_count_range"][0] = int(word_count * 0.9)
        elif word_count > current_max * 1.2:
            prefs["writing_style"]["word_count_range"][1] = int(word_count * 1.1)

    if category:
        # 更新历史统计
        history = prefs["history_summary"]
        history["total_articles"] += 1
        history["last_topic_category"] = category
        history["common_categories"][category] = (
            history["common_categories"].get(category, 0) + 1
        )

    save_preferences(prefs)


def record_topic(topic: str) -> None:
    """记录用户写过的主题"""
    prefs = load_preferences()
    history = prefs["history_summary"]
    history["last_topic"] = topic
    history["common_topics"][topic] = history["common_topics"].get(topic, 0) + 1
    save_preferences(prefs)


def get_common_categories() -> list:
    """获取最常用的分类"""
    prefs = load_preferences()
    categories = prefs["history_summary"]["common_categories"]
    return sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]


def get_recommended_style() -> str:
    """获取推荐的文章风格"""
    return get("writing_style.preferred_style", "tech")


def get_cover_theme() -> str:
    """获取偏好的封面主题"""
    return get("cover_preferences.preferred_theme", "blue")


def reset_preferences() -> None:
    """重置偏好到默认值"""
    if PREFERENCES_FILE.exists():
        PREFERENCES_FILE.unlink()
    save_preferences(DEFAULT_PREFERENCES.copy())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="用户偏好记忆管理工具")
    parser.add_argument("--get", metavar="KEY", help="获取偏好值，如: writing_style.preferred_style")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="设置偏好值，如: writing_style.preferred_style minimal")
    parser.add_argument("--record-topic", metavar="TOPIC", help="记录写作主题")
    parser.add_argument("--update-style", metavar="STYLE", help="更新写作风格 (tech/minimal/business)")
    parser.add_argument("--update-category", metavar="CATEGORY", help="更新写作分类")
    parser.add_argument("--show", action="store_true", help="显示所有偏好")
    parser.add_argument("--reset", action="store_true", help="重置所有偏好")
    parser.add_argument("--common", action="store_true", help="显示常用分类")

    args = parser.parse_args()

    if args.show:
        prefs = load_preferences()
        print("=== 用户偏好 ===")
        import json
        print(json.dumps(prefs, ensure_ascii=False, indent=2))

    elif args.reset:
        confirm = input("确认重置所有偏好？(y/n): ")
        if confirm.lower() == "y":
            reset_preferences()
            print("偏好已重置")

    elif args.get:
        value = get(args.get)
        print(f"{args.get}: {value}")

    elif args.set:
        set_value(args.set[0], args.set[1])
        print(f"已设置: {args.set[0]} = {args.set[1]}")

    elif args.record_topic:
        record_topic(args.record_topic)
        print(f"已记录主题: {args.record_topic}")

    elif args.update_style:
        update_writing_feedback(style=args.update_style)
        print(f"已更新写作风格: {args.update_style}")

    elif args.update_category:
        update_writing_feedback(category=args.update_category)
        print(f"已更新分类: {args.update_category}")

    elif args.common:
        print("=== 常用分类 ===")
        for cat, count in get_common_categories():
            print(f"  {cat}: {count} 篇")

    else:
        parser.print_help()
