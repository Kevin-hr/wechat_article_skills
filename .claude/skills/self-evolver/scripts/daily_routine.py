#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 每日例行程序
每日运行：追踪 → 健康检查 → 生成报告 → HTML报告 → 自动优化 → Git提交
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# 添加脚本路径
SELF_EVOLVER_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SELF_EVOLVER_DIR / "scripts"))

from usage_tracker import init_data_dir, load_metrics, get_success_rate
from health_checker import HealthChecker
from report_generator import ReportGenerator
from html_report import HTMLReportGenerator
from skills_optimizer import SkillsLinkageOptimizer
from auto_updater import AutoUpdater
from git_automation import GitAutomation


def run_daily_routine():
    """运行每日例行程序"""
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"Skills 每日例行程序")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    results = {
        "timestamp": datetime.now().isoformat(),
        "steps": [],
        "success": True
    }

    try:
        # Step 1: 初始化
        print("[1/6] 初始化...")
        init_data_dir()
        results["steps"].append({"step": "init", "status": "ok"})
        print("[OK]\n")

        # Step 2: 健康检查
        print("[2/6] 健康检查...")
        checker = HealthChecker()
        health_report = checker.check_all()
        checker.print_report()
        results["steps"].append({
            "step": "health_check",
            "status": "ok",
            "passed": health_report["passed"],
            "warnings": health_report["warnings"],
            "failed": health_report["failed"]
        })
        print()

        # Step 3: 修复问题
        print("[3/6] 自动修复...")
        updater = AutoUpdater()
        issues = updater.analyze_issues(health_report)
        fix_results = updater.apply_updates(issues, dry_run=False)
        results["steps"].append({
            "step": "auto_fix",
            "applied": len(fix_results.get("applied", [])),
            "skipped": len(fix_results.get("skipped", []))
        })
        print()

        # Step 4: 生成报告
        print("[4/6] 生成复盘报告...")
        generator = ReportGenerator()
        report = generator.generate_weekly_report()
        generator.print_report(report)
        generator.save_report(report)
        results["steps"].append({"step": "report", "status": "ok"})
        print()

        # Step 5: HTML 可视化报告
        print("[5/6] 生成 HTML 可视化报告...")
        html_gen = HTMLReportGenerator()
        html_content = html_gen.generate_daily_report()
        html_path = html_gen.save_report(html_content, "daily")
        print(f"[OK] 报告已保存: {html_path}")
        results["steps"].append({"step": "html_report", "status": "ok"})
        print()

        # Step 6: Git 提交
        print("[6/6] Git 提交...")
        git = GitAutomation()
        git.auto_commit_daily()
        results["steps"].append({"step": "git_commit", "status": "ok"})
        print()

    except Exception as e:
        print(f"[FAIL] 错误: {e}")
        results["success"] = False
        results["error"] = str(e)

    # 汇总
    duration = time.time() - start_time
    results["duration"] = duration

    print(f"{'='*60}")
    print(f"每日例行程序完成!")
    print(f"耗时: {duration:.2f} 秒")
    print(f"成功率: {get_success_rate():.1f}%")
    print(f"{'='*60}\n")

    return results


def run_weekly_routine():
    """运行每周例行程序（包含优化建议）"""
    results = run_daily_routine()

    print("\n[额外] 技能优化分析...")
    optimizer = SkillsLinkageOptimizer()
    report = optimizer.generate_optimization_report()
    optimizer.print_report(report)

    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--weekly":
        run_weekly_routine()
    else:
        run_daily_routine()
