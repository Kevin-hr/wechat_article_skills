#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 联动优化器
自动优化低使用率技能，根据使用数据调整配置
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent))
from usage_tracker import load_metrics, init_data_dir

# 目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SELF_EVOLVER_DIR.parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"


class SkillsLinkageOptimizer:
    """Skills 联动优化器"""

    def __init__(self):
        self.metrics = load_metrics()
        self.skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

    def analyze_low_usage_skills(self, threshold: int = 3, days: int = 30) -> List[Dict]:
        """分析低使用率技能"""
        cutoff = datetime.now() - timedelta(days=days)
        low_usage = []

        for skill_dir in self.skill_dirs:
            skill_name = skill_dir.name
            m = self.metrics.get(skill_name, {"total_calls": 0})

            if m["total_calls"] < threshold:
                # 检查是否从未被追踪
                if skill_name not in self.metrics:
                    low_usage.append({
                        "skill": skill_name,
                        "calls": 0,
                        "reason": "从未被使用",
                        "action": "考虑删除或合并"
                    })
                else:
                    low_usage.append({
                        "skill": skill_name,
                        "calls": m["total_calls"],
                        "reason": f"近{days}天仅使用 {m['total_calls']} 次",
                        "action": "建议优化或合并"
                    })

        return low_usage

    def analyze_high_failure_skills(self, threshold: float = 0.2) -> List[Dict]:
        """分析高失败率技能"""
        high_failure = []

        for skill_name, m in self.metrics.items():
            if m["total_calls"] > 0:
                failure_rate = m["failure_count"] / m["total_calls"]
                if failure_rate > threshold:
                    high_failure.append({
                        "skill": skill_name,
                        "failure_rate": failure_rate * 100,
                        "failure_count": m["failure_count"],
                        "total_calls": m["total_calls"],
                        "action": "检查 SKILL.md 和脚本配置"
                    })

        return high_failure

    def auto_optimize_low_usage(self, dry_run: bool = True) -> Dict:
        """自动优化低使用率技能"""
        results = {"optimized": [], "skipped": [], "failed": []}

        low_usage = self.analyze_low_usage_skills(threshold=3, days=30)

        for item in low_usage:
            skill_name = item["skill"]
            skill_dir = SKILLS_DIR / skill_name

            # 优化建议：检查 SKILL.md 是否需要更新
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")

                # 检查是否有 trigger 字段
                if "trigger:" not in content:
                    if not dry_run:
                        # 添加使用建议到文档
                        suggestion = f"\n\n> ⚠️ 此技能使用率较低，请考虑优化或删除。\n"
                        content += suggestion
                        skill_md.write_text(content, encoding="utf-8")

                    results["optimized"].append({
                        "skill": skill_name,
                        "action": "添加使用警告提示",
                        "details": "在 SKILL.md 中添加了低使用率警告"
                    })
                else:
                    results["skipped"].append({
                        "skill": skill_name,
                        "reason": "已配置 trigger，可能只是未触发"
                    })
            else:
                results["skipped"].append({
                    "skill": skill_name,
                    "reason": "缺少 SKILL.md"
                })

        return results

    def suggest_skill_merge(self) -> List[Dict]:
        """建议合并相似技能"""
        # 基于名称相似性分组
        skill_groups = {}
        for skill_dir in self.skill_dirs:
            skill_name = skill_dir.name
            # 提取前缀
            parts = skill_name.split("-")
            if len(parts) >= 2:
                prefix = parts[0]
                if prefix not in skill_groups:
                    skill_groups[prefix] = []
                skill_groups[prefix].append(skill_name)

        # 找出只有一个技能的分组
        suggestions = []
        for prefix, skills in skill_groups.items():
            if len(skills) == 1:
                m = self.metrics.get(skills[0], {"total_calls": 0})
                if m["total_calls"] < 5:  # 低使用率
                    suggestions.append({
                        "group": prefix,
                        "skill": skills[0],
                        "calls": m["total_calls"],
                        "suggestion": f"技能 '{skills[0]}' 可能过于细分，考虑合并到通用技能"
                    })

        return suggestions

    def generate_optimization_report(self) -> Dict:
        """生成优化报告"""
        low_usage = self.analyze_low_usage_skills(threshold=3, days=30)
        high_failure = self.analyze_high_failure_skills(threshold=0.2)
        merge_suggestions = self.suggest_skill_merge()

        return {
            "generated_at": datetime.now().isoformat(),
            "low_usage_skills": low_usage,
            "high_failure_skills": high_failure,
            "merge_suggestions": merge_suggestions,
            "total_issues": len(low_usage) + len(high_failure),
            "priority_actions": self._prioritize_actions(low_usage, high_failure)
        }

    def _prioritize_actions(self, low_usage: List, high_failure: List) -> List[Dict]:
        """优先级排序"""
        actions = []

        # 高失败率优先处理
        for item in high_failure:
            actions.append({
                "priority": "HIGH",
                "skill": item["skill"],
                "issue": f"失败率 {item['failure_rate']:.1f}%",
                "action": "立即检查配置和脚本"
            })

        # 低使用率次之
        for item in low_usage:
            actions.append({
                "priority": "MEDIUM" if item["calls"] > 0 else "LOW",
                "skill": item["skill"],
                "issue": f"仅使用 {item['calls']} 次",
                "action": item["action"]
            })

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        return sorted(actions, key=lambda x: priority_order.get(x["priority"], 99))

    def auto_apply_optimizations(self, dry_run: bool = True) -> Dict:
        """自动应用优化"""
        results = {
            "dry_run": dry_run,
            "optimizations_applied": [],
            "suggestions": []
        }

        # 1. 自动优化低使用率技能
        low_opt_results = self.auto_optimize_low_usage(dry_run=dry_run)
        results["optimizations_applied"].extend(low_opt_results.get("optimized", []))

        # 2. 生成优化建议
        report = self.generate_optimization_report()
        results["suggestions"] = report["priority_actions"]

        return results

    def print_report(self, report: Dict):
        """打印报告"""
        print(f"\n=== Skills 优化报告 ===")
        print(f"生成时间: {report['generated_at'][:19]}")

        # 低使用率
        if report["low_usage_skills"]:
            print(f"\n低使用率技能 ({len(report['low_usage_skills'])} 个):")
            for item in report["low_usage_skills"]:
                print(f"  - {item['skill']}: {item['reason']}")

        # 高失败率
        if report["high_failure_skills"]:
            print(f"\n高失败率技能 ({len(report['high_failure_skills'])} 个):")
            for item in report["high_failure_skills"]:
                print(f"  - {item['skill']}: {item['failure_rate']:.1f}% 失败率")

        # 合并建议
        if report["merge_suggestions"]:
            print(f"\n合并建议 ({len(report['merge_suggestions'])} 个):")
            for item in report["merge_suggestions"]:
                print(f"  - {item['skill']}: {item['suggestion']}")

        # 优先级操作
        if report["priority_actions"]:
            print(f"\n优先级操作:")
            for action in report["priority_actions"][:5]:  # 只显示前5个
                print(f"  [{action['priority']}] {action['skill']}: {action['action']}")


def main():
    parser = argparse.ArgumentParser(description="Skills 联动优化器")
    parser.add_argument("--analyze", action="store_true", help="分析优化建议")
    parser.add_argument("--auto", action="store_true", help="自动应用优化")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")

    args = parser.parse_args()

    init_data_dir()
    optimizer = SkillsLinkageOptimizer()

    if args.analyze:
        report = optimizer.generate_optimization_report()
        optimizer.print_report(report)
    elif args.auto:
        results = optimizer.auto_apply_optimizations(dry_run=args.dry_run)
        if args.dry_run:
            print("[DRY RUN] 预览优化内容:")
        print(f"应用优化: {len(results['optimizations_applied'])}")
        print(f"建议操作: {len(results['suggestions'])}")
    else:
        report = optimizer.generate_optimization_report()
        optimizer.print_report(report)


if __name__ == "__main__":
    main()
