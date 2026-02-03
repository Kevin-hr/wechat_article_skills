#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 自我进化系统 - 主入口
整合使用追踪、健康检查、定期复盘、自动更新
"""

import argparse
import sys
from pathlib import Path

# 添加脚本路径
SCRIPTS_DIR = Path(__file__).parent


def run_all():
    """运行完整的进化流程"""
    print("=" * 60)
    print("Skills 自我进化系统 - 完整流程")
    print("=" * 60)

    # 1. 使用追踪
    print("\n[1/4] 运行使用追踪...")
    import importlib.util
    spec = importlib.util.spec_from_file_location("usage_tracker", SCRIPTS_DIR / "usage_tracker.py")
    tracker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tracker)
    tracker.init_data_dir()
    tracker.show_stats(7)

    # 2. 健康检查
    print("\n[2/4] 运行健康检查...")
    spec = importlib.util.spec_from_file_location("health_checker", SCRIPTS_DIR / "health_checker.py")
    checker_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker_mod)
    checker = checker_mod.HealthChecker()
    health_report = checker.check_all()
    checker.print_report()

    # 3. 生成复盘报告
    print("\n[3/4] 生成复盘报告...")
    spec = importlib.util.spec_from_file_location("report_generator", SCRIPTS_DIR / "report_generator.py")
    generator_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator_mod)
    generator = generator_mod.ReportGenerator()
    report = generator.generate_weekly_report()
    generator.print_report(report)
    generator.save_report(report)

    # 4. 自动更新
    print("\n[4/4] 检查自动更新...")
    spec = importlib.util.spec_from_file_location("auto_updater", SCRIPTS_DIR / "auto_updater.py")
    updater_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(updater_mod)
    updater = updater_mod.AutoUpdater()
    issues = updater.analyze_issues(health_report)
    preview = updater.preview_updates(issues)

    print(f"\n发现 {len(issues)} 个问题")
    print(f"可自动修复: {preview['auto_fixable']}")

    if preview['auto_fixable'] > 0:
        print("\n使用 --apply 参数应用自动修复")
        print("使用 --dry-run 参数预览变更")

    print("\n" + "=" * 60)
    print("进化流程完成!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Skills 自我进化系统",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # track 命令
    track_parser = subparsers.add_parser("track", help="追踪使用情况")
    track_parser.add_argument("--skill", "-s", required=True, help="技能名称")
    track_parser.add_argument("--status", choices=["success", "fail"], default="success")
    track_parser.add_argument("--duration", "-d", type=float, default=0.0)

    # stats 命令
    subparsers.add_parser("stats", help="显示使用统计")

    # health 命令
    subparsers.add_parser("health", help="运行健康检查")

    # report 命令
    report_parser = subparsers.add_parser("report", help="生成复盘报告")
    report_parser.add_argument("--weekly", action="store_true")
    report_parser.add_argument("--monthly", action="store_true")
    report_parser.add_argument("--save", action="store_true")

    # update 命令
    update_parser = subparsers.add_parser("update", help="自动更新 Skills")
    update_parser.add_argument("--dry-run", action="store_true")
    update_parser.add_argument("--apply", action="store_true")
    update_parser.add_argument("--script", action="store_true")

    # all 命令
    subparsers.add_parser("all", help="运行完整进化流程")

    args = parser.parse_args()

    if args.command == "track":
        import importlib.util
        spec = importlib.util.spec_from_file_location("usage_tracker", SCRIPTS_DIR / "usage_tracker.py")
        tracker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tracker)
        tracker.init_data_dir()
        tracker.manual_record(args.skill, args.status, args.duration)

    elif args.command == "stats":
        import importlib.util
        spec = importlib.util.spec_from_file_location("usage_tracker", SCRIPTS_DIR / "usage_tracker.py")
        tracker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tracker)
        tracker.init_data_dir()
        tracker.show_stats(args.days if hasattr(args, 'days') else 7)

    elif args.command == "health":
        import importlib.util
        spec = importlib.util.spec_from_file_location("health_checker", SCRIPTS_DIR / "health_checker.py")
        checker_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_mod)
        checker = checker_mod.HealthChecker()
        results = checker.check_all()
        checker.print_report()
        sys.exit(0 if results["failed"] == 0 else 1)

    elif args.command == "report":
        import importlib.util
        spec = importlib.util.spec_from_file_location("report_generator", SCRIPTS_DIR / "report_generator.py")
        generator_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator_mod)
        generator = generator_mod.ReportGenerator()
        generator.init_data_dir()

        if args.monthly:
            report = generator.generate_monthly_report()
        else:
            report = generator.generate_weekly_report()

        generator.print_report(report)
        if args.save:
            generator.save_report(report)

    elif args.command == "update":
        import importlib.util
        spec = importlib.util.spec_from_file_location("health_checker", SCRIPTS_DIR / "health_checker.py")
        checker_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_mod)

        spec = importlib.util.spec_from_file_location("auto_updater", SCRIPTS_DIR / "auto_updater.py")
        updater_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(updater_mod)

        checker = checker_mod.HealthChecker()
        health_report = checker.check_all()

        updater = updater_mod.AutoUpdater()
        issues = updater.analyze_issues(health_report)
        preview = updater.preview_updates(issues)

        print(f"\n发现 {len(issues)} 个问题")
        print(f"可自动修复: {preview['auto_fixable']}")
        print(f"需手动处理: {preview['manual_required']}")

        if args.script:
            script_path = updater.generate_update_script(issues)
            print(f"\n[OK] 更新脚本已生成: {script_path}")
        elif args.apply or args.dry_run:
            results = updater.apply_updates(issues, dry_run=args.dry_run)
            updater.print_results(results)
        else:
            print("\n使用 --apply 应用更新")
            print("使用 --dry-run 预览")

    elif args.command == "all":
        run_all()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
