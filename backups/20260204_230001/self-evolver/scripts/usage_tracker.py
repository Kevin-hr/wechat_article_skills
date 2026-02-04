#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 使用追踪器
记录 Skills 的调用日志、使用频率、成功率等
支持自动集成追踪
"""

import argparse
import functools
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

# 数据目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
DATA_DIR = SELF_EVOLVER_DIR / "data"
USAGE_LOG = DATA_DIR / "usage_log.json"
METRICS_FILE = DATA_DIR / "metrics.json"


def init_data_dir():
    """初始化数据目录"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USAGE_LOG.exists():
        USAGE_LOG.write_text("[]", encoding="utf-8")
    if not METRICS_FILE.exists():
        METRICS_FILE.write_text("{}", encoding="utf-8")


def load_usage_log() -> List[Dict]:
    """加载使用日志"""
    if USAGE_LOG.exists():
        with open(USAGE_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_usage_log(log: List[Dict]):
    """保存使用日志"""
    with open(USAGE_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def load_metrics() -> Dict:
    """加载指标数据"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_metrics(metrics: Dict):
    """保存指标数据"""
    with open(METRICS_FILE, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)


def get_success_rate(metrics: Dict = None) -> float:
    """获取全局成功率"""
    if metrics is None:
        metrics = load_metrics()
    total = sum(m.get("total_calls", 0) for m in metrics.values())
    success = sum(m.get("success_count", 0) for m in metrics.values())
    return (success / total * 100) if total > 0 else 0.0


def track_usage(skill_name: str, success: bool = True, duration: float = 0.0, notes: str = ""):
    """追踪单次使用"""
    init_data_dir()
    log = load_usage_log()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "skill": skill_name,
        "success": success,
        "duration_seconds": duration,
        "notes": notes
    }

    log.append(entry)

    # 更新指标
    metrics = load_metrics()
    if skill_name not in metrics:
        metrics[skill_name] = {
            "total_calls": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_duration": 0.0,
            "last_called": None,
            "first_called": None
        }

    m = metrics[skill_name]
    m["total_calls"] += 1
    if success:
        m["success_count"] += 1
    else:
        m["failure_count"] += 1
    m["total_duration"] += duration
    m["last_called"] = entry["timestamp"]
    if m["first_called"] is None:
        m["first_called"] = entry["timestamp"]

    save_usage_log(log)
    save_metrics(metrics)

    print(f"[OK] 已记录: {skill_name} (成功: {success})")


def auto_track(skill_name: str = None):
    """自动追踪装饰器 - 用于集成到其他 Skills

    使用方式:
        from usage_tracker import auto_track

        @auto_track("my-skill")
        def main():
            ...

        # 或自动从函数名推断
        @auto_track()
        def wechat_tech_writer():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_msg = ""
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                duration = time.time() - start_time
                name = skill_name or func.__name__
                # 转换函数名为 skill 格式: wechat_tech_writer -> wechat-tech-writer
                skill_id = name.replace("_", "-")
                track_usage(skill_id, success, duration, error_msg)
        return wrapper
    return decorator


def track_skill(skill_name: str, success: bool = True, duration: float = 0.0):
    """便捷追踪函数 - 集成到 Skills 主入口

    在 Skills 的 main.py 或入口函数中调用:
        from usage_tracker import track_skill

        if __name__ == "__main__":
            track_skill("wechat-tech-writer", success=True, duration=2.5)
            # 或包装整个 main 函数
            track_and_run()
    """
    track_usage(skill_name, success, duration)


def show_stats(days: int = 7):
    """显示统计信息"""
    metrics = load_metrics()
    log = load_usage_log()

    # 过滤最近 N 天的数据
    cutoff = datetime.now() - timedelta(days=days)
    recent_logs = [
        entry for entry in log
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff
    ]

    print(f"\n=== Skills 使用统计 (最近 {days} 天) ===")
    print(f"总调用次数: {len(recent_logs)}")

    # 按调用次数排序
    sorted_skills = sorted(metrics.items(), key=lambda x: x[1]["total_calls"], reverse=True)

    print(f"\n{'技能名称':<30} {'调用次数':<10} {'成功率':<10} {'平均耗时':<10}")
    print("-" * 60)

    for skill_name, m in sorted_skills:
        success_rate = (m["success_count"] / m["total_calls"] * 100) if m["total_calls"] > 0 else 0
        avg_duration = (m["total_duration"] / m["total_calls"]) if m["total_calls"] > 0 else 0
        print(f"{skill_name:<30} {m['total_calls']:<10} {success_rate:.1f}%{'':<6} {avg_duration:.2f}s")

    # 列出最近 N 条日志
    print(f"\n=== 最近日志 ===")
    for entry in recent_logs[-10:]:
        status = "[OK]" if entry["success"] else "[FAIL]"
        time = entry["timestamp"][:19]
        print(f"{status} {time} - {entry['skill']}")


def export_report(days: int = 7) -> Dict:
    """导出报告数据"""
    metrics = load_metrics()
    log = load_usage_log()

    cutoff = datetime.now() - timedelta(days=days)
    recent_logs = [
        entry for entry in log
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff
    ]

    report = {
        "period_days": days,
        "generated_at": datetime.now().isoformat(),
        "total_calls": len(recent_logs),
        "unique_skills_used": len(set(e["skill"] for e in recent_logs)),
        "metrics": metrics,
        "success_rate": len([e for e in recent_logs if e["success"]]) / max(len(recent_logs), 1) * 100
    }

    return report


def manual_record(skill_name: str, status: str = "success", duration: float = 0.0):
    """手动记录一次使用"""
    success = status.lower() in ["success", "ok", "true", "1"]
    track_usage(skill_name, success, duration)


def main():
    parser = argparse.ArgumentParser(description="Skills 使用追踪器")
    parser.add_argument("--track", "-t", help="追踪特定技能使用")
    parser.add_argument("--status", "-s", help="记录特定技能状态 (success/fail)")
    parser.add_argument("--duration", "-d", type=float, default=0.0, help="耗时（秒）")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--days", type=int, default=7, help="统计天数（默认7）")
    parser.add_argument("--export", action="store_true", help="导出报告数据")

    args = parser.parse_args()

    init_data_dir()

    if args.track:
        manual_record(args.track, args.status or "success", args.duration)
    elif args.stats:
        show_stats(args.days)
    elif args.export:
        report = export_report(args.days)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        # 默认显示帮助和统计
        show_stats(args.days)


if __name__ == "__main__":
    main()
