"""
多平台发布模块

支持将文章发布到微信公众号、知乎、掘金、头条号等平台。
存储位置: ~/.wechat-writer/platforms.json
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

# 存储路径
PLATFORMS_DIR = Path(os.path.expanduser("~/.wechat-writer"))
PLATFORMS_FILE = PLATFORMS_DIR / "platforms.json"


@dataclass
class PlatformConfig:
    """平台配置"""
    name: str  # 显示名称
    platform_id: str  # 平台标识
    enabled: bool = True
    # 微信公众号
    wechat_appid: Optional[str] = None
    wechat_appsecret: Optional[str] = None
    # 知乎
    zhihu_token: Optional[str] = None
    # 掘金
    juejin_token: Optional[str] = None
    # 头条号
    toutiao_token: Optional[str] = None
    # 通用字段
    default_tags: List[str] = None
    auto_publish: bool = False
    last_sync: Optional[str] = None


# 默认平台配置
DEFAULT_PLATFORMS = {
    "wechat": PlatformConfig(
        name="微信公众号",
        platform_id="wechat",
        enabled=True,
        default_tags=["AI", "技术"],
        auto_publish=False,
    ),
    "zhihu": PlatformConfig(
        name="知乎",
        platform_id="zhihu",
        enabled=False,
        default_tags=["人工智能", "AI"],
        auto_publish=False,
    ),
    "juejin": PlatformConfig(
        name="掘金",
        platform_id="juejin",
        enabled=False,
        default_tags=["AI", "产品"],
        auto_publish=False,
    ),
    "toutiao": PlatformConfig(
        name="头条号",
        platform_id="toutiao",
        enabled=False,
        default_tags=["AI", "科技"],
        auto_publish=False,
    ),
}


def ensure_storage_dir():
    """确保存储目录存在"""
    PLATFORMS_DIR.mkdir(parents=True, exist_ok=True)


def load_platforms() -> Dict[str, Any]:
    """加载平台配置"""
    ensure_storage_dir()
    if PLATFORMS_FILE.exists():
        try:
            with open(PLATFORMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_platforms(platforms: Dict[str, Any]) -> None:
    """保存平台配置"""
    ensure_storage_dir()
    with open(PLATFORMS_FILE, "w", encoding="utf-8") as f:
        json.dump(platforms, f, ensure_ascii=False, indent=2)


def get_platform(platform_id: str) -> Optional[Dict]:
    """获取单个平台配置"""
    platforms = load_platforms()
    if platform_id in platforms:
        return platforms[platform_id]
    # 返回默认配置
    if platform_id in DEFAULT_PLATFORMS:
        return asdict(DEFAULT_PLATFORMS[platform_id])
    return None


def enable_platform(platform_id: str, token: str = None, **kwargs) -> bool:
    """启用平台并设置 token"""
    platforms = load_platforms()
    platform_id = platform_id.lower()

    if platform_id not in DEFAULT_PLATFORMS:
        return False

    platforms[platform_id] = asdict(DEFAULT_PLATFORMS[platform_id])
    platforms[platform_id]["enabled"] = True
    platforms[platform_id]["last_sync"] = datetime.now().isoformat()

    if token:
        # 根据平台选择字段
        if platform_id == "wechat":
            platforms[platform_id]["wechat_appid"] = token.split(":")[0] if ":" in token else token
            platforms[platform_id]["wechat_appsecret"] = token.split(":")[1] if ":" in token else None
        elif platform_id == "zhihu":
            platforms[platform_id]["zhihu_token"] = token
        elif platform_id == "juejin":
            platforms[platform_id]["juejin_token"] = token
        elif platform_id == "toutiao":
            platforms[platform_id]["toutiao_token"] = token

    # 更新其他设置
    for key, value in kwargs.items():
        if key in platforms[platform_id]:
            platforms[platform_id][key] = value

    save_platforms(platforms)
    return True


def disable_platform(platform_id: str) -> bool:
    """禁用平台"""
    platforms = load_platforms()
    platform_id = platform_id.lower()
    if platform_id in platforms:
        platforms[platform_id]["enabled"] = False
        save_platforms(platforms)
        return True
    return False


def list_enabled_platforms() -> List[Dict]:
    """列出已启用的平台"""
    platforms = load_platforms()
    enabled = []
    for pid, config in platforms.items():
        if config.get("enabled", False):
            name = config.get("name", pid)
            enabled.append({
                "id": pid,
                "name": name,
                "tags": config.get("default_tags", []),
                "last_sync": config.get("last_sync"),
            })
    return enabled


def get_all_platforms() -> List[Dict]:
    """获取所有平台（包括未启用）"""
    platforms = load_platforms()
    all_platforms = []

    # 合并默认配置
    for pid, default in DEFAULT_PLATFORMS.items():
        if pid in platforms:
            config = platforms[pid]
        else:
            config = asdict(default)
        all_platforms.append({
            "id": pid,
            "name": config["name"],
            "enabled": config.get("enabled", False),
            "tags": config.get("default_tags", []),
        })

    return all_platforms


def update_last_sync(platform_id: str) -> None:
    """更新最后同步时间"""
    platforms = load_platforms()
    platform_id = platform_id.lower()
    if platform_id in platforms:
        platforms[platform_id]["last_sync"] = datetime.now().isoformat()
        save_platforms(platforms)


# 发布函数占位符
def publish_to_wechat(title: str, content: str, cover: str = None, author: str = "雲帆AI") -> Dict:
    """发布到微信公众号"""
    # 实际实现调用 wechat-draft-publisher
    return {
        "platform": "wechat",
        "status": "pending",
        "message": "调用 wechat-draft-publisher 发布",
    }


def publish_to_zhihu(title: str, content: str, tags: List[str] = None) -> Dict:
    """发布到知乎"""
    # 知乎 API 需要 OAuth2 认证
    return {
        "platform": "zhihu",
        "status": "todo",
        "message": "需要实现知乎 OAuth2 发布",
    }


def publish_to_juejin(title: str, content: str, tags: List[str] = None) -> Dict:
    """发布到掘金"""
    # 掘金使用 X-Juejin-Sdk 认证
    return {
        "platform": "juejin",
        "status": "todo",
        "message": "需要实现掘金 API 发布",
    }


def publish_to_toutiao(title: str, content: str, tags: List[str] = None) -> Dict:
    """发布到头条号"""
    # 头条号 API
    return {
        "platform": "toutiao",
        "status": "todo",
        "message": "需要实现头条号 API 发布",
    }


def publish_multi_platform(title: str, content: str, platforms: List[str] = None,
                           cover: str = None, author: str = "雲帆AI") -> Dict:
    """多平台同步发布"""
    if platforms is None:
        enabled = list_enabled_platforms()
        platforms = [p["id"] for p in enabled]

    results = {}
    for pid in platforms:
        if pid == "wechat":
            results["wechat"] = publish_to_wechat(title, content, cover, author)
        elif pid == "zhihu":
            config = get_platform("zhihu")
            tags = config.get("default_tags", []) if config else []
            results["zhihu"] = publish_to_zhihu(title, content, tags)
        elif pid == "juejin":
            config = get_platform("juejin")
            tags = config.get("default_tags", []) if config else []
            results["juejin"] = publish_to_juejin(title, content, tags)
        elif pid == "toutiao":
            config = get_platform("toutiao")
            tags = config.get("default_tags", []) if config else []
            results["toutiao"] = publish_to_toutiao(title, content, tags)

    return {
        "total": len(platforms),
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="多平台发布管理")
    parser.add_argument("--list", action="store_true", help="列出所有平台")
    parser.add_argument("--enabled", action="store_true", help="列出已启用的平台")
    parser.add_argument("--enable", metavar="PLATFORM", help="启用平台，如: wechat, zhihu")
    parser.add_argument("--disable", metavar="PLATFORM", help="禁用平台")
    parser.add_argument("--status", action="store_true", help="显示所有平台状态")

    args = parser.parse_args()

    if args.status:
        print("=== 平台状态 ===")
        for p in get_all_platforms():
            status = "[启用]" if p["enabled"] else "[未启用]"
            print(f"  {p['name']} ({p['id']}): {status}")

    elif args.list:
        print("=== 所有平台 ===")
        for p in get_all_platforms():
            print(f"  {p['id']}: {p['name']}")

    elif args.enabled:
        print("=== 已启用平台 ===")
        for p in list_enabled_platforms():
            print(f"  {p['name']} ({p['id']}) - 标签: {', '.join(p['tags'])}")

    elif args.enable:
        success = enable_platform(args.enable)
        if success:
            print(f"已启用平台: {args.enable}")
        else:
            print(f"无效平台: {args.enable}")

    elif args.disable:
        success = disable_platform(args.disable)
        if success:
            print(f"已禁用平台: {args.disable}")
        else:
            print(f"无效平台: {args.disable}")

    else:
        parser.print_help()
