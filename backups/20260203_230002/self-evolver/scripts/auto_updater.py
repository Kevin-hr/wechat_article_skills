#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 自动更新器
根据健康检查和复盘报告自动优化 Skills
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 项目根目录 - 从当前文件向上查找
SELF_EVOLVER_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SELF_EVOLVER_DIR.parent.parent.parent  # wechat_article_skills/
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"


class AutoUpdater:
    """Skills 自动更新器"""

    def __init__(self):
        self.changes = []
        self.backup_dir = PROJECT_ROOT / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")

    def analyze_issues(self, health_report: Dict = None) -> List[Dict]:
        """分析需要修复的问题"""
        issues = []

        if health_report is None:
            # 运行健康检查
            from health_checker import HealthChecker
            checker = HealthChecker()
            health_report = checker.check_all()

        # 分析每个 Skill 的问题
        for detail in health_report.get("details", []):
            skill = detail["skill"]

            for error in detail.get("errors", []):
                issues.append({
                    "skill": skill,
                    "type": "error",
                    "description": error,
                    "auto_fixable": self._is_auto_fixable(error, skill)
                })

            for warning in detail.get("warnings", []):
                issues.append({
                    "skill": skill,
                    "type": "warning",
                    "description": warning,
                    "auto_fixable": self._is_auto_fixable(warning, skill)
                })

        return issues

    def _is_auto_fixable(self, issue: str, skill: str) -> bool:
        """判断问题是否可自动修复"""
        auto_fixable_patterns = [
            "缺少 YAML frontmatter",
            "YAML frontmatter 格式错误",
            "缺少 name 字段",
            "缺少 description 字段",
            "引用的 MD 文件不存在",
            "引用的脚本不存在",
            "空脚本文件",
            "references/ 目录中的文件未被引用",
            "缺少 references 目录"
        ]
        return any(pattern in issue for pattern in auto_fixable_patterns)

    def preview_updates(self, issues: List[Dict]) -> Dict:
        """预览更新内容"""
        preview = {
            "total_issues": len(issues),
            "auto_fixable": len([i for i in issues if i["auto_fixable"]]),
            "manual_required": len([i for i in issues if not i["auto_fixable"]]),
            "proposed_changes": []
        }

        for issue in issues:
            if issue["auto_fixable"]:
                change = self._generate_fix(issue)
                if change:
                    preview["proposed_changes"].append(change)

        return preview

    def _generate_fix(self, issue: Dict) -> Optional[Dict]:
        """生成修复方案"""
        skill = issue["skill"]
        skill_dir = SKILLS_DIR / skill
        description = issue["description"]

        # 缺少 references 目录
        if "缺少 references 目录" in description:
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(exist_ok=True)
            return {
                "skill": skill,
                "action": "create_directory",
                "path": str(refs_dir),
                "description": "创建 references 目录"
            }

        # 引用的 MD 文件不存在
        if "引用的 MD 文件不存在" in description:
            match = description.split(": ")[-1]
            ref_path = skill_dir / match
            ref_path.parent.mkdir(parents=True, exist_ok=True)
            ref_path.write_text("# " + match.replace(".md", "") + "\n")
            return {
                "skill": skill,
                "action": "create_file",
                "path": str(ref_path),
                "description": f"创建缺失的引用文件: {match}"
            }

        # 空脚本文件
        if "空脚本文件" in description:
            filename = description.split(": ")[-1]
            return {
                "skill": skill,
                "action": "delete_file",
                "path": str(skill_dir / "scripts" / filename),
                "description": f"删除空脚本: {filename}"
            }

        return None

    def apply_updates(self, issues: List[Dict], dry_run: bool = True) -> Dict:
        """应用更新"""
        results = {
            "applied": [],
            "skipped": [],
            "failed": [],
            "dry_run": dry_run
        }

        if dry_run:
            print("[DRY RUN] 预览模式，不会实际修改文件\n")

        # 先创建备份
        if not dry_run:
            self._create_backup()

        for issue in issues:
            if not issue["auto_fixable"]:
                results["skipped"].append(issue)
                continue

            change = self._generate_fix(issue)
            if not change:
                results["skipped"].append(issue)
                continue

            if dry_run:
                print(f"[PREVIEW] {change['description']}")
                print(f"  -> {change['action']}: {change['path']}\n")
                results["applied"].append(change)
            else:
                try:
                    self._execute_change(change)
                    print(f"[OK] {change['description']}")
                    results["applied"].append(change)
                except Exception as e:
                    print(f"[FAIL] {change['description']}: {e}")
                    results["failed"].append({"issue": issue, "error": str(e)})

        return results

    def _execute_change(self, change: Dict):
        """执行变更"""
        action = change["action"]
        path = Path(change["path"])

        if action == "create_directory":
            path.mkdir(parents=True, exist_ok=True)
        elif action == "create_file":
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("# " + path.stem + "\n")
        elif action == "delete_file":
            if path.exists():
                path.unlink()

    def _create_backup(self):
        """创建备份"""
        print(f"[BACKUP] 创建备份: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 备份所有 Skills
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                backup_skill = self.backup_dir / skill_dir.name
                import shutil
                shutil.copytree(skill_dir, backup_skill)

        print(f"[OK] 备份完成\n")

    def optimize_skill_content(self, skill_name: str, suggestions: List[str]) -> Dict:
        """根据建议优化 Skill 内容"""
        skill_dir = SKILLS_DIR / skill_name
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            return {"error": "SKILL.md 不存在"}

        original_content = skill_md.read_text(encoding="utf-8")
        optimized_content = original_content

        # 应用建议
        for suggestion in suggestions:
            # 示例：拆分长文档
            if "拆分" in suggestion and "references" in suggestion:
                # 添加 references 目录引用
                if "## 详细指南" in optimized_content:
                    optimized_content = optimized_content.replace(
                        "## 详细指南",
                        "## 详细指南\n\n详见 [references/](../references/)\n"
                    )

        if optimized_content != original_content:
            if not (skill_dir / "references").exists():
                (skill_dir / "references").mkdir(exist_ok=True)

            skill_md.write_text(optimized_content, encoding="utf-8")
            return {
                "action": "updated",
                "file": str(skill_md),
                "changes": len(suggestions)
            }

        return {"action": "no_changes", "file": str(skill_md)}

    def print_results(self, results: Dict):
        """打印结果"""
        print(f"\n=== 自动更新结果 ===")

        if results.get("dry_run"):
            print("模式: 预览 (dry run)\n")

        print(f"应用: {len(results.get('applied', []))}")
        print(f"跳过: {len(results.get('skipped', []))}")
        print(f"失败: {len(results.get('failed', []))}")

        if results.get("applied"):
            print(f"\n已应用的变更:")
            for change in results["applied"]:
                print(f"  - {change['description']}")

    def generate_update_script(self, issues: List[Dict]) -> str:
        """生成手动更新脚本"""
        script_lines = [
            "#!/bin/bash",
            "# Skills 自动更新脚本",
            f"# 生成时间: {datetime.now().isoformat()}",
            "",
            "set -e",
            ""
        ]

        for issue in issues:
            if not issue["auto_fixable"]:
                continue

            skill = issue["skill"]
            description = issue["description"]

            if "缺少 references 目录" in description:
                script_lines.append(f"# {skill}: 创建 references 目录")
                script_lines.append(f"mkdir -p .claude/skills/{skill}/references")
                script_lines.append("")

            elif "空脚本文件" in description:
                filename = description.split(": ")[-1]
                script_lines.append(f"# {skill}: 删除空脚本")
                script_lines.append(f"rm -f .claude/skills/{skill}/scripts/{filename}")
                script_lines.append("")

        script_lines.append("echo '更新完成'")
        script_content = "\n".join(script_lines)

        script_path = PROJECT_ROOT / "scripts" / "update_skills.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script_content, encoding="utf-8")

        return str(script_path)


def main():
    parser = argparse.ArgumentParser(description="Skills 自动更新器")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际修改")
    parser.add_argument("--apply", action="store_true", help="应用更新")
    parser.add_argument("--script", action="store_true", help="生成手动更新脚本")
    parser.add_argument("--health", action="store_true", help="先运行健康检查")

    args = parser.parse_args()

    updater = AutoUpdater()

    # 运行健康检查
    if args.health:
        from health_checker import HealthChecker
        print("运行健康检查...")
        checker = HealthChecker()
        health_report = checker.check_all()
        checker.print_report()
    else:
        health_report = None

    # 分析问题
    print("\n分析问题...")
    issues = updater.analyze_issues(health_report)
    print(f"发现 {len(issues)} 个问题")

    if args.script:
        script_path = updater.generate_update_script(issues)
        print(f"\n[OK] 更新脚本已生成: {script_path}")
        return

    # 预览更新
    preview = updater.preview_updates(issues)
    print(f"\n可自动修复: {preview['auto_fixable']}")
    print(f"需手动处理: {preview['manual_required']}")

    # 应用更新
    if args.apply or args.dry_run:
        results = updater.apply_updates(issues, dry_run=args.dry_run)
        updater.print_results(results)


if __name__ == "__main__":
    main()
