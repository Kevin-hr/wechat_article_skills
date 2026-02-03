#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills Git 自动化脚本
自动提交 Skills 变更，记录版本历史
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
PROJECT_ROOT = SELF_EVOLVER_DIR.parent.parent


class GitAutomation:
    """Git 自动化工具"""

    def __init__(self):
        self.repo = PROJECT_ROOT

    def run_git(self, *args) -> tuple:
        """执行 git 命令"""
        result = subprocess.run(
            ["git"] + list(args),
            cwd=self.repo,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def get_status(self) -> Dict:
        """获取 git 状态"""
        code, stdout, stderr = self.run_git("status", "--porcelain")
        lines = stdout.strip().split("\n") if stdout.strip() else []
        changes = [line[3:] for line in lines if line]

        code, stdout, _ = self.run_git("status", "-sb")
        branch = stdout.split("\n")[0].replace("## ", "").split("...")[0]

        return {
            "branch": branch,
            "changes": changes,
            "is_clean": len(changes) == 0
        }

    def stage_all(self) -> bool:
        """暂存所有变更"""
        code, _, stderr = self.run_git("add", "-A")
        return code == 0

    def commit(self, message: str) -> bool:
        """提交变更"""
        self.stage_all()
        code, _, stderr = self.run_git("commit", "-m", message)
        if code != 0:
            print(f"提交失败: {stderr}")
        return code == 0

    def commit_skills_update(self, report_type: str = "daily") -> bool:
        """提交 Skills 更新"""
        status = self.get_status()
        if status["is_clean"]:
            print("没有需要提交的变更")
            return False

        date = datetime.now().strftime("%Y-%m-%d")
        message = f"chore(self-evolver): {report_type} skills update {date}"

        return self.commit(message)

    def commit_health_fix(self, skill_name: str, fix_type: str) -> bool:
        """提交健康检查修复"""
        message = f"fix(self-evolver): {fix_type} for {skill_name}"
        return self.commit(message)

    def push(self, branch: str = None) -> bool:
        """推送变更"""
        if branch is None:
            status = self.get_status()
            branch = status["branch"]

        code, _, stderr = self.run_git("push", "origin", branch)
        if code != 0:
            print(f"推送失败: {stderr}")
        return code == 0

    def create_backup_tag(self) -> bool:
        """创建备份标签"""
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        tag = f"backup-{date}"

        code, _, stderr = self.run_git("tag", "-a", tag, "-m", f"Skills backup {date}")
        if code == 0:
            print(f"[OK] 标签已创建: {tag}")
            return True
        print(f"创建标签失败: {stderr}")
        return False

    def log_skills_changes(self, days: int = 7) -> List[Dict]:
        """获取 Skills 变更日志"""
        since = datetime.now().strftime(f"%Y-%m-%d 00:00:00")
        # 减去 days 天
        from datetime import timedelta
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        code, stdout, _ = self.run_git("log", f"--since={since_date}", "--oneline", "--", ".claude/skills/")
        lines = stdout.strip().split("\n") if stdout.strip() else []

        commits = []
        for line in lines:
            if line:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1]
                    })

        return commits

    def auto_commit_daily(self) -> bool:
        """每日自动提交"""
        # 1. 检查是否有变更
        status = self.get_status()
        if status["is_clean"]:
            print("没有需要提交的变更")
            return True

        # 2. 获取今日指标
        data_file = SELF_EVOLVER_DIR / "data" / "metrics.json"
        metrics_summary = ""
        if data_file.exists():
            metrics = json.loads(data_file.read_text(encoding="utf-8"))
            total = sum(m.get("total_calls", 0) for m in metrics.values())
            success = sum(m.get("success_count", 0) for m in metrics.values())
            rate = (success / total * 100) if total > 0 else 0
            metrics_summary = f" (调用: {total}, 成功率: {rate:.1f}%)"

        # 3. 提交
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"chore(self-evolver): daily skills snapshot {date}{metrics_summary}"

        return self.commit(message)

    def generate_changelog(self, days: int = 30) -> str:
        """生成更新日志"""
        commits = self.log_skills_changes(days)

        changelog = f"""# Skills 更新日志

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**统计周期**: 最近 {days} 天

## 变更记录

"""

        for c in commits:
            changelog += f"- `{c['hash'][:8]}` {c['message']}\n"

        return changelog


def main():
    parser = argparse.ArgumentParser(description="Skills Git 自动化")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--commit", action="store_true", help="提交所有变更")
    parser.add_argument("--daily", action="store_true", help="每日自动提交")
    parser.add_argument("--push", action="store_true", help="推送到远程")
    parser.add_argument("--tag", action="store_true", help="创建备份标签")
    parser.add_argument("--log", action="store_true", help="查看变更日志")
    parser.add_argument("--changelog", action="store_true", help="生成更新日志")

    args = parser.parse_args()

    git = GitAutomation()

    if args.status:
        status = git.get_status()
        print(f"分支: {status['branch']}")
        print(f"变更: {status['changes']}")
        print(f"干净: {'是' if status['is_clean'] else '否'}")

    elif args.commit:
        message = f"chore(self-evolver): skills update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if git.commit(message):
            print("[OK] 提交成功")
            if args.push:
                git.push()

    elif args.daily:
        if git.auto_commit_daily():
            print("[OK] 每日提交完成")

    elif args.push:
        if git.push():
            print("[OK] 推送成功")

    elif args.tag:
        git.create_backup_tag()

    elif args.log:
        commits = git.log_skills_changes()
        print(f"最近 {len(commits)} 条变更:")
        for c in commits:
            print(f"  {c['hash'][:8]} {c['message']}")

    elif args.changelog:
        changelog = git.generate_changelog()
        print(changelog)


if __name__ == "__main__":
    main()
