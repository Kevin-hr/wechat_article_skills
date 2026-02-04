#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 复盘报告生成器
定期生成使用统计、优化建议、进化方向的报告
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 导入追踪器
sys.path.insert(0, str(Path(__file__).parent))
from usage_tracker import load_metrics, load_usage_log, init_data_dir

# 目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
REPORTS_DIR = SELF_EVOLVER_DIR / "reports"
PROJECT_ROOT = SELF_EVOLVER_DIR.parent.parent.parent  # wechat_article_skills/


class ReportGenerator:
    """复盘报告生成器"""

    def __init__(self):
        self.metrics = load_metrics()
        self.usage_log = load_usage_log()
        self.recommendations = []

    def generate_weekly_report(self) -> Dict:
        """生成周报"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # 过滤本周数据
        weekly_logs = [
            entry for entry in self.usage_log
            if datetime.fromisoformat(entry["timestamp"]) >= start_date
        ]

        report = {
            "type": "weekly",
            "period": f"{start_date.date()} ~ {end_date.date()}",
            "generated_at": datetime.now().isoformat(),
            "summary": self._generate_summary(weekly_logs),
            "usage_analysis": self._analyze_usage(weekly_logs),
            "performance_metrics": self._analyze_performance(),
            "recommendations": self._generate_recommendations(),
            "evolution_suggestions": self._generate_evolution_suggestions()
        }

        return report

    def generate_monthly_report(self) -> Dict:
        """生成月报"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        monthly_logs = [
            entry for entry in self.usage_log
            if datetime.fromisoformat(entry["timestamp"]) >= start_date
        ]

        report = {
            "type": "monthly",
            "period": f"{start_date.date()} ~ {end_date.date()}",
            "generated_at": datetime.now().isoformat(),
            "summary": self._generate_summary(monthly_logs),
            "trend_analysis": self._analyze_trends(monthly_logs),
            "top_performers": self._get_top_performers(),
            "underperformers": self._get_underperformers(),
            "recommendations": self._generate_recommendations(),
            "quarterly_goals": self._generate_quarterly_goals()
        }

        return report

    def _generate_summary(self, logs: List[Dict]) -> Dict:
        """生成摘要"""
        total_calls = len(logs)
        success_count = len([e for e in logs if e["success"]])
        unique_skills = set(e["skill"] for e in logs)

        return {
            "total_calls": total_calls,
            "success_rate": round(success_count / max(total_calls, 1) * 100, 1),
            "unique_skills_used": len(unique_skills),
            "most_used_skill": self._get_most_used(logs),
            "least_used_skill": self._get_least_used(logs)
        }

    def _analyze_usage(self, logs: List[Dict]) -> Dict:
        """分析使用情况"""
        skill_counts = {}
        for entry in logs:
            skill = entry["skill"]
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "skill_usage_ranking": sorted_skills[:10],
            "peak_hours": self._analyze_peak_hours(logs),
            "success_by_skill": self._get_success_by_skill(logs)
        }

    def _analyze_performance(self) -> Dict:
        """分析性能指标"""
        performances = {}
        for skill, m in self.metrics.items():
            if m["total_calls"] > 0:
                performances[skill] = {
                    "avg_duration": round(m["total_duration"] / m["total_calls"], 2),
                    "success_rate": round(m["success_count"] / m["total_calls"] * 100, 1),
                    "total_calls": m["total_calls"]
                }
        return performances

    def _get_most_used(self, logs: List[Dict]) -> str:
        """获取最常用技能"""
        if not logs:
            return "N/A"
        counts = {}
        for e in logs:
            counts[e["skill"]] = counts.get(e["skill"], 0) + 1
        return max(counts, key=counts.get)

    def _get_least_used(self, logs: List[Dict]) -> str:
        """获取最少使用技能"""
        if not logs:
            return "N/A"
        counts = {}
        for e in logs:
            counts[e["skill"]] = counts.get(e["skill"], 0) + 1
        return min(counts, key=counts.get)

    def _analyze_peak_hours(self, logs: List[Dict]) -> List:
        """分析高峰期"""
        hours = [datetime.fromisoformat(e["timestamp"]).hour for e in logs]
        hour_counts = {}
        for h in hours:
            hour_counts[h] = hour_counts.get(h, 0) + 1
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [{"hour": h, "count": c} for h, c in sorted_hours]

    def _get_success_by_skill(self, logs: List[Dict]) -> Dict:
        """获取每个技能的成功率"""
        success_by_skill = {}
        for e in logs:
            skill = e["skill"]
            if skill not in success_by_skill:
                success_by_skill[skill] = {"total": 0, "success": 0}
            success_by_skill[skill]["total"] += 1
            if e["success"]:
                success_by_skill[skill]["success"] += 1

        return {
            skill: {
                "total": data["total"],
                "success_rate": round(data["success"] / data["total"] * 100, 1)
            }
            for skill, data in success_by_skill.items()
        }

    def _get_top_performers(self) -> List:
        """获取表现最好的技能"""
        sorted_skills = sorted(
            self.metrics.items(),
            key=lambda x: x[1]["total_calls"],
            reverse=True
        )[:5]
        return [{"skill": s, "calls": m["total_calls"]} for s, m in sorted_skills]

    def _get_underperformers(self) -> List:
        """获取表现不佳的技能"""
        # 找出调用次数少或失败率高的
        underperformers = []
        for skill, m in self.metrics.items():
            if m["total_calls"] == 0:
                underperformers.append({"skill": skill, "issue": "从未使用"})
            elif m["failure_count"] > m["success_count"]:
                underperformers.append({"skill": skill, "issue": "失败率过高"})
        return underperformers

    def _generate_recommendations(self) -> List:
        """生成优化建议"""
        recommendations = []

        # 基于使用情况的建议
        if self.metrics:
            sorted_skills = sorted(
                self.metrics.items(),
                key=lambda x: x[1]["total_calls"],
                reverse=True
            )

            if sorted_skills:
                top = sorted_skills[0][0]
                recommendations.append(f"重点优化 '{top}'，它是使用最频繁的技能")

            # 找出未使用的技能
            skills_dir = PROJECT_ROOT / ".claude" / "skills"
            skill_names = [d.name for d in skills_dir.iterdir() if d.is_dir()]
            used_skills = set(self.metrics.keys())
            unused = [s for s in skill_names if s not in used_skills]
            if unused:
                recommendations.append(f"以下技能从未被使用，考虑优化或删除: {', '.join(unused)}")

        return recommendations

    def _generate_evolution_suggestions(self) -> List:
        """生成进化建议"""
        suggestions = []

        # 检查是否有长期未更新的技能
        skills_dir = PROJECT_ROOT / ".claude" / "skills"
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    # 检查是否有 references 目录
                    if not (skill_dir / "references").exists():
                        suggestions.append(f"'{skill_dir.name}' 缺少 references 目录，建议拆分长文档")

        return suggestions

    def _analyze_trends(self, logs: List[Dict]) -> Dict:
        """分析趋势"""
        # 按天统计
        daily_counts = {}
        for entry in logs:
            date = entry["timestamp"][:10]
            daily_counts[date] = daily_counts.get(date, 0) + 1

        sorted_days = sorted(daily_counts.items())
        trend = "up" if len(sorted_days) > 1 and daily_counts[sorted_days[-1][0]] > daily_counts[sorted_days[0][0]] else "down"

        return {
            "daily_usage": sorted_days,
            "trend": trend,
            "avg_daily_calls": round(sum(daily_counts.values()) / max(len(daily_counts), 1), 1)
        }

    def _generate_quarterly_goals(self) -> List:
        """生成季度目标"""
        return [
            "提升 Skills 整体成功率至 98% 以上",
            "优化使用频率最低的 3 个技能",
            "为高频技能添加更多 references 文档",
            "建立 Skills 调用数据的可视化仪表盘"
        ]

    def print_report(self, report: Dict):
        """打印报告"""
        print(f"\n=== Skills {report['type'].upper()} 复盘报告 ===")
        print(f"周期: {report['period']}")
        print(f"生成时间: {report['generated_at'][:19]}")

        # 摘要
        summary = report.get("summary", {})
        print(f"\n--- 摘要 ---")
        print(f"总调用次数: {summary.get('total_calls', 'N/A')}")
        print(f"成功率: {summary.get('success_rate', 'N/A')}%")
        print(f"使用技能数: {summary.get('unique_skills_used', 'N/A')}")
        print(f"最常用: {summary.get('most_used_skill', 'N/A')}")
        print(f"最少用: {summary.get('least_used_skill', 'N/A')}")

        # 使用分析
        usage = report.get("usage_analysis", {})
        if usage:
            print(f"\n--- 使用排行 TOP 5 ---")
            for skill, count in usage.get("skill_usage_ranking", [])[:5]:
                print(f"  {skill}: {count} 次")

        # 建议
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n--- 优化建议 ---")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        # 进化建议
        evolution = report.get("evolution_suggestions", [])
        if evolution:
            print(f"\n--- 进化方向 ---")
            for i, sug in enumerate(evolution, 1):
                print(f"  {i}. {sug}")

    def save_report(self, report: Dict):
        """保存报告"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{report['type']}_{report['period'].replace(' ', '_')}.json"
        filepath = REPORTS_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n[INFO] 报告已保存: {filepath}")
        return filepath


def main():
    parser = argparse.ArgumentParser(description="Skills 复盘报告生成器")
    parser.add_argument("--weekly", action="store_true", help="生成本周报")
    parser.add_argument("--monthly", action="store_true", help="生成本月报")
    parser.add_argument("--save", action="store_true", help="保存报告到文件")

    args = parser.parse_args()

    init_data_dir()

    generator = ReportGenerator()

    if args.monthly:
        report = generator.generate_monthly_report()
    else:
        report = generator.generate_weekly_report()

    generator.print_report(report)

    if args.save:
        generator.save_report(report)


if __name__ == "__main__":
    main()
