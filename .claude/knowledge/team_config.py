"""
团队协作配置模块

支持团队成员共享配置、写作规范和模板。
存储位置: ~/.wechat-writer/team.json (本地)
团队配置可同步到项目目录: .wechat-writer/team.json
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict, field

# 存储路径
LOCAL_DIR = Path(os.path.expanduser("~/.wechat-writer"))
TEAM_LOCAL_FILE = LOCAL_DIR / "team.json"
PROJECT_TEAM_FILE = Path(".wechat-writer/team.json")


@dataclass
class TeamMember:
    """团队成员"""
    id: str
    name: str
    role: str  # admin, editor, writer
    email: Optional[str] = None
    preferences: Dict = field(default_factory=dict)
    last_active: Optional[str] = None


@dataclass
class TeamConfig:
    """团队配置"""
    team_id: str
    team_name: str
    members: List[Dict] = field(default_factory=list)
    shared_templates: Dict = field(default_factory=dict)
    writing_rules: Dict = field(default_factory=dict)
    common_tags: List[str] = field(default_factory=list)
    default_author: str = "雲帆AI"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# 默认写作规则
DEFAULT_WRITING_RULES = {
    "title": {
        "max_length": 64,
        "min_length": 8,
        "forbidden_chars": ["!", "？", "……"],
    },
    "author": {
        "max_length": 20,
        "allowed_format": "中文/英文/英文+中文",
    },
    "digest": {
        "max_length": 120,
        "min_length": 30,
    },
    "cover": {
        "min_width": 900,
        "min_height": 383,
        "max_size_mb": 2,
        "formats": ["png", "jpg"],
    },
    "content": {
        "min_words": 500,
        "max_words": 5000,
        "require_cover": True,
        "require_tags": True,
    },
}


def ensure_storage_dir():
    """确保存储目录存在"""
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)


def load_team_config() -> Dict[str, Any]:
    """加载团队配置（优先本地，项目目录次之）"""
    # 优先从项目目录加载（支持版本控制）
    if PROJECT_TEAM_FILE.exists():
        try:
            with open(PROJECT_TEAM_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # 从本地加载
    ensure_storage_dir()
    if TEAM_LOCAL_FILE.exists():
        try:
            with open(TEAM_LOCAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {}


def save_team_config(config: Dict, local: bool = True) -> None:
    """保存团队配置"""
    config["updated_at"] = datetime.now().isoformat()

    if local:
        ensure_storage_dir()
        with open(TEAM_LOCAL_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    else:
        # 保存到项目目录
        PROJECT_TEAM_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROJECT_TEAM_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)


def init_team(team_name: str, team_id: str = None) -> Dict:
    """初始化团队配置"""
    team_id = team_id or team_name.lower().replace(" ", "-")

    config = {
        "team_id": team_id,
        "team_name": team_name,
        "members": [],
        "shared_templates": {},
        "writing_rules": DEFAULT_WRITING_RULES,
        "common_tags": ["AI", "技术"],
        "default_author": "雲帆AI",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    save_team_config(config, local=False)
    return config


def add_member(member: Dict) -> bool:
    """添加团队成员"""
    config = load_team_config()
    if "members" not in config:
        config["members"] = []

    # 检查是否已存在
    for m in config["members"]:
        if m.get("id") == member["id"]:
            return False

    config["members"].append({
        **member,
        "last_active": datetime.now().isoformat(),
    })
    save_team_config(config, local=False)
    return True


def remove_member(member_id: str) -> bool:
    """移除团队成员"""
    config = load_team_config()
    if "members" not in config:
        return False

    original_len = len(config["members"])
    config["members"] = [m for m in config["members"] if m.get("id") != member_id]

    if len(config["members"]) < original_len:
        save_team_config(config, local=False)
        return True
    return False


def get_member(member_id: str) -> Optional[Dict]:
    """获取成员信息"""
    config = load_team_config()
    for m in config.get("members", []):
        if m.get("id") == member_id:
            return m
    return None


def list_members() -> List[Dict]:
    """列出所有成员"""
    config = load_team_config()
    return config.get("members", [])


def update_writing_rules(rules: Dict) -> None:
    """更新写作规则"""
    config = load_team_config()
    config["writing_rules"] = {**config.get("writing_rules", {}), **rules}
    save_team_config(config, local=False)


def add_shared_template(name: str, template: Dict) -> None:
    """添加共享模板"""
    config = load_team_config()
    if "shared_templates" not in config:
        config["shared_templates"] = {}
    config["shared_templates"][name] = {
        **template,
        "created_at": datetime.now().isoformat(),
    }
    save_team_config(config, local=False)


def get_template(name: str) -> Optional[Dict]:
    """获取共享模板"""
    config = load_team_config()
    return config.get("shared_templates", {}).get(name)


def list_templates() -> List[str]:
    """列出所有共享模板"""
    config = load_team_config()
    return list(config.get("shared_templates", {}).keys())


def add_common_tag(tag: str) -> None:
    """添加常用标签"""
    config = load_team_config()
    if "common_tags" not in config:
        config["common_tags"] = []
    if tag not in config["common_tags"]:
        config["common_tags"].append(tag)
        save_team_config(config, local=False)


def get_common_tags() -> List[str]:
    """获取常用标签"""
    config = load_team_config()
    return config.get("common_tags", [])


def validate_article(article: Dict) -> Dict:
    """根据团队规则验证文章"""
    config = load_team_config()
    rules = config.get("writing_rules", DEFAULT_WRITING_RULES)

    errors = []
    warnings = []

    # 验证标题
    title = article.get("title", "")
    title_rules = rules.get("title", {})
    if len(title) > title_rules.get("max_length", 64):
        errors.append(f"标题过长: {len(title)} > {title_rules['max_length']} 字符")
    if len(title) < title_rules.get("min_length", 8):
        warnings.append(f"标题过短: {len(title)} < {title_rules['min_length']} 字符")

    # 验证作者
    author = article.get("author", "")
    author_rules = rules.get("author", {})
    if len(author.encode()) > author_rules.get("max_length", 20):
        errors.append(f"作者名过长: {len(author.encode())} > {author_rules['max_length']} 字节")

    # 验证摘要
    digest = article.get("digest", "")
    digest_rules = rules.get("digest", {})
    if len(digest) > digest_rules.get("max_length", 120):
        errors.append(f"摘要过长: {len(digest)} > {digest_rules['max_length']} 字符")

    # 验证内容
    content = article.get("content", "")
    content_rules = rules.get("content", {})
    word_count = len(content)
    if word_count < content_rules.get("min_words", 500):
        warnings.append(f"内容过短: {word_count} < {content_rules['min_words']} 字")
    if word_count > content_rules.get("max_words", 5000):
        warnings.append(f"内容过长: {word_count} > {content_rules['max_words']} 字")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0, 100 - len(errors) * 20 - len(warnings) * 5),
    }


def sync_from_cloud(cloud_config: Dict) -> None:
    """从云端同步配置（占位）"""
    # 实际实现可以连接共享配置服务器或 Git
    save_team_config(cloud_config, local=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="团队协作配置管理")
    parser.add_argument("--init", nargs=2, metavar=("TEAM_NAME", "TEAM_ID"), help="初始化团队配置")
    parser.add_argument("--members", action="store_true", help="列出团队成员")
    parser.add_argument("--templates", action="store_true", help="列出共享模板")
    parser.add_argument("--tags", action="store_true", help="列出常用标签")
    parser.add_argument("--validate", metavar="FILE", help="验证文章文件 (JSON)")

    args = parser.parse_args()

    if args.init:
        config = init_team(args.init[0], args.init[1] if len(args.init) > 1 else None)
        print(f"团队已初始化: {config['team_name']} (ID: {config['team_id']})")

    elif args.members:
        print("=== 团队成员 ===")
        for m in list_members():
            print(f"  {m['name']} ({m['role']}) - {m.get('email', '无邮箱')}")

    elif args.templates:
        print("=== 共享模板 ===")
        for t in list_templates():
            print(f"  {t}")

    elif args.tags:
        print("=== 常用标签 ===")
        print(f"  {', '.join(get_common_tags())}")

    elif args.validate:
        with open(args.validate, "r", encoding="utf-8") as f:
            article = json.load(f)
        result = validate_article(article)
        print(f"验证结果: {'[通过]' if result['valid'] else '[失败]'}")
        if result["errors"]:
            print("错误:", result["errors"])
        if result["warnings"]:
            print("警告:", result["warnings"])
        print(f"评分: {result['score']}/100")

    else:
        parser.print_help()
