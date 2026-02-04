#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 健康检查器
检查 SKILL.md 格式、引用完整性、脚本可用性
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 项目根目录 - 从当前文件向上查找项目根目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SELF_EVOLVER_DIR.parent.parent.parent  # wechat_article_skills/
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"


class HealthChecker:
    """Skills 健康检查器"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_checked": 0,
            "passed": 0,
            "warnings": 0,
            "failed": 0,
            "details": []
        }

    def check_all(self) -> Dict:
        """检查所有 Skills"""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            self.check_skill(skill_dir)

        # 汇总
        self.results["total_checked"] = len(self.results["details"])
        self.results["passed"] = len([d for d in self.results["details"] if d["status"] == "pass"])
        self.results["warnings"] = len([d for d in self.results["details"] if d["status"] == "warning"])
        self.results["failed"] = len([d for d in self.results["details"] if d["status"] == "fail"])

        return self.results

    def check_skill(self, skill_dir: Path):
        """检查单个 Skill"""
        skill_name = skill_dir.name
        result = {
            "skill": skill_name,
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }

        # 1. 检查 SKILL.md 是否存在
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            result["status"] = "fail"
            result["errors"].append("缺少 SKILL.md")
            self.results["details"].append(result)
            return

        # 2. 检查 SKILL.md 格式
        self._check_skill_format(skill_dir, skill_md, result)

        # 3. 检查引用完整性
        self._check_references(skill_dir, skill_md, result)

        # 4. 检查 scripts 目录
        self._check_scripts(skill_dir, result)

        # 5. 检查 references 目录
        self._check_references_dir(skill_dir, result)

        # 更新状态
        if result["errors"]:
            result["status"] = "fail"
        elif result["warnings"]:
            result["status"] = "warning"

        self.results["details"].append(result)

    def _check_skill_format(self, skill_dir: Path, skill_md: Path, result: Dict):
        """检查 SKILL.md 格式"""
        content = skill_md.read_text(encoding="utf-8")

        # 检查 YAML frontmatter
        if not content.startswith("---"):
            result["errors"].append("缺少 YAML frontmatter")
            return

        # 提取 frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            result["errors"].append("YAML frontmatter 格式错误")
            return

        frontmatter = match.group(1)
        if "name:" not in frontmatter:
            result["errors"].append("缺少 name 字段")
        if "description:" not in frontmatter:
            result["errors"].append("缺少 description 字段")

        result["checks"].append("YAML frontmatter 格式正确")

    def _check_references(self, skill_dir: Path, skill_md: Path, result: Dict):
        """检查 SKILL.md 中的引用"""
        content = skill_md.read_text(encoding="utf-8")

        # 查找 markdown 链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)

        for link_text, link_path in links:
            if link_path.startswith("#"):
                continue  # 跳过锚点

            # 检查相对路径引用
            if link_path.endswith(".md"):
                # 转换为实际路径
                ref_path = skill_dir / link_path
                if not ref_path.exists():
                    result["warnings"].append(f"引用的 MD 文件不存在: {link_path}")

            # 检查脚本引用
            if link_path.startswith("scripts/"):
                script_path = skill_dir / link_path
                if not script_path.exists():
                    result["warnings"].append(f"引用的脚本不存在: {link_path}")

    def _check_scripts(self, skill_dir: Path, result: Dict):
        """检查 scripts 目录"""
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.exists():
            return

        # 检查脚本是否有执行权限（跳过检查 Windows）
        for script in scripts_dir.glob("*.py"):
            if script.stat().st_size == 0:
                result["warnings"].append(f"空脚本文件: {script.name}")

    def _check_references_dir(self, skill_dir: Path, result: Dict):
        """检查 references 目录"""
        refs_dir = skill_dir / "references"
        if not refs_dir.exists():
            return

        # 检查是否有孤立文件（未被 SKILL.md 引用）
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            for ref_file in refs_dir.glob("*.md"):
                # 检查文件名是否在 SKILL.md 中被引用
                if ref_file.name not in content:
                    result["warnings"].append(f"references/ 目录中的文件未被引用: {ref_file.name}")

    def print_report(self):
        """打印检查报告"""
        print(f"\n=== Skills 健康检查报告 ===")
        print(f"日期: {self.results['timestamp'][:10]}")
        print(f"\n检查总数: {self.results['total_checked']}")
        print(f"通过: {self.results['passed']}")
        print(f"警告: {self.results['warnings']}")
        print(f"失败: {self.results['failed']}")

        if self.results["warnings"]:
            print(f"\n警告列表:")
            for detail in self.results["details"]:
                if detail["warnings"]:
                    print(f"- {detail['skill']}:")
                    for w in detail["warnings"][:3]:  # 只显示前3个
                        print(f"  - {w}")

        if self.results["failed"]:
            print(f"\n失败列表:")
            for detail in self.results["details"]:
                if detail["errors"]:
                    print(f"- {detail['skill']}:")
                    for e in detail["errors"]:
                        print(f"  - {e}")

        # 保存报告
        report_file = PROJECT_ROOT / "logs" / "health_check_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] 报告已保存: {report_file}")

        return self.results


def main():
    parser = argparse.ArgumentParser(description="Skills 健康检查器")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复")

    args = parser.parse_args()

    checker = HealthChecker()
    results = checker.check_all()

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        checker.print_report()

    # 返回退出码
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
