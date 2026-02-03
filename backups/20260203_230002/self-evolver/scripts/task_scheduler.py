#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 定时任务配置
支持 Windows schtasks 和 Linux/Mac cron
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SELF_EVOLVER_DIR.parent.parent


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.scripts_dir = SELF_EVOLVER_DIR / "scripts"

    def setup_daily_tasks(self):
        """配置每日任务"""
        python = sys.executable
        script_path = self.scripts_dir / "daily_routine.py"

        if os.name == "nt":  # Windows
            self._setup_windows_daily(python, script_path)
        else:  # Linux/Mac
            self._setup_cron_daily(python, script_path)

    def _setup_windows_daily(self, python: str, script_path: str):
        """Windows 每日任务配置"""
        task_name = "SkillsSelfEvolverDaily"
        time_str = "23:00"  # 每天晚上11点

        # 创建每日任务脚本
        cmd = f'schtasks /create /tn "{task_name}" /tr "{python} {script_path}" /sc daily /st {time_str} /f'

        print(f"[Windows] 创建每日任务...")
        print(f"命令: {cmd}")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] 每日任务已创建: 每天 {time_str} 执行")
        else:
            print(f"[FAIL] 创建失败: {result.stderr}")

    def _setup_cron_daily(self, python: str, script_path: str):
        """Linux/Mac 每日任务配置"""
        cron_time = "0 23 * * *"  # 每天晚上11点
        cron_cmd = f'{cron_time} {python} {script_path}'

        print(f"[Cron] 添加每日任务...")
        print(f"命令: {cron_cmd}")

        # 获取当前 crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        if "SkillsSelfEvolverDaily" not in current_cron:
            new_cron = current_cron + f"\n{cron_cmd}\n"
            subprocess.run(["crontab", "-"], input=new_cron, capture_output=True, text=True)
            print("[OK] 每日任务已添加")
        else:
            print("[INFO] 任务已存在")

    def remove_daily_tasks(self):
        """删除每日任务"""
        if os.name == "nt":
            subprocess.run('schtasks /delete /tn "SkillsSelfEvolverDaily" /f', shell=True)
            print("[OK] Windows 任务已删除")
        else:
            # 从 crontab 移除
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                cron_lines = [l for l in result.stdout.split("\n") if "SkillsSelfEvolverDaily" not in l]
                subprocess.run(["crontab", "-"], input="\n".join(cron_lines), capture_output=True, text=True)
                print("[OK] Cron 任务已删除")

    def show_status(self):
        """显示任务状态"""
        if os.name == "nt":
            result = subprocess.run('schtasks /query /tn "SkillsSelfEvolverDaily"', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("[OK] Windows 任务存在")
            else:
                print("[INFO] Windows 任务不存在")
        else:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if "SkillsSelfEvolverDaily" in result.stdout:
                print("[OK] Cron 任务存在")
            else:
                print("[INFO] Cron 任务不存在")


def main():
    parser = argparse.ArgumentParser(description="Skills 定时任务配置")
    parser.add_argument("--setup", action="store_true", help="配置每日任务")
    parser.add_argument("--remove", action="store_true", help="删除每日任务")
    parser.add_argument("--status", action="store_true", help="查看任务状态")

    args = parser.parse_args()

    scheduler = TaskScheduler()

    if args.status:
        scheduler.show_status()
    elif args.setup:
        scheduler.setup_daily_tasks()
    elif args.remove:
        scheduler.remove_daily_tasks()
    else:
        print("Usage:")
        print("  --setup   配置每日任务")
        print("  --remove  删除每日任务")
        print("  --status  查看任务状态")


if __name__ == "__main__":
    main()
