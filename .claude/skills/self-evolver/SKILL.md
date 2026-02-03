---
name: self-evolver
description: Skills 自我进化系统。自动追踪使用情况、定期复盘分析、健康检查、自动更新优化、可视化报告、Git自动化。
---

# Skills 自我进化系统

## 核心功能

| 功能 | 说明 | 命令 |
|------|------|------|
| 使用追踪 | 自动记录 Skills 调用，成功率为核心指标 | 自动集成到其他 Skills |
| 健康检查 | 检查 SKILL.md 格式、引用完整性 | `python scripts/main.py health` |
| HTML 报告 | 可视化仪表盘展示关键信息 | `python scripts/html_report.py --daily --save` |
| 自动修复 | 自动修复配置问题 | `python scripts/main.py update --apply` |
| 技能联动 | 自动优化低使用率技能 | `python scripts/skills_optimizer.py --auto` |
| Git 自动化 | 自动提交变更 | `python scripts/git_automation.py --daily` |
| 每日例行 | 一键运行完整流程 | `python scripts/daily_routine.py` |

## 系统架构

```
自动追踪 → 数据存储 → 可视化报告 → 自动优化 → Git提交
    │           │           │           │          │
usage_    metrics.json   html_      skills_    git_
tracker.py  usage_log.py report.py  optimizer  automation
```

## 快速开始

```bash
cd .claude/skills/self-evolver

# 1. 配置每日定时任务（推荐）
python scripts/task_scheduler.py --setup

# 2. 查看成功率
python scripts/main.py stats

# 3. 运行完整例行程序
python scripts/daily_routine.py
```

## 集成到其他 Skills

### 方式1：装饰器（推荐）
```python
# 在 Skills 的 main.py 中
from usage_tracker import auto_track

@auto_track("my-skill")
def main():
    # 你的技能逻辑
    ...

if __name__ == "__main__":
    main()
```

### 方式2：函数调用
```python
from usage_tracker import track_skill

if __name__ == "__main__":
    try:
        # 执行技能逻辑
        result = do_something()
        track_skill("my-skill", success=True, duration=2.5)
    except Exception as e:
        track_skill("my-skill", success=False, duration=0)
        raise
```

## 每日复盘

### 一键运行每日例行程序
```bash
python scripts/daily_routine.py
```

包含：健康检查 → 自动修复 → 复盘报告 → HTML报告 → Git提交

### 查看成功率
```bash
python scripts/main.py stats --days 1   # 今天
python scripts/main.py stats --days 7   # 最近7天
```

### HTML 可视化报告
```bash
python scripts/html_report.py --daily --save   # 日报
python scripts/html_report.py --weekly --save  # 周报
python scripts/html_report.py --monthly --save # 月报
```

打开 `reports/daily_YYYY-MM-DD.html` 查看可视化仪表盘。

## 指标说明

| 指标 | 说明 | 关注度 |
|------|------|--------|
| **成功率** | success_count / total_calls | ⭐ 核心 |
| 总调用次数 | total_calls | 辅助 |
| 平均耗时 | total_duration / total_calls | 辅助 |

**目标**: 成功率 ≥ 95%

## 技能联动优化

自动分析并优化低使用率技能：

```bash
# 分析优化建议
python scripts/skills_optimizer.py --analyze

# 自动应用优化（预览）
python scripts/skills_optimizer.py --auto --dry-run

# 自动应用优化（实际执行）
python scripts/skills_optimizer.py --auto
```

## Git 自动化

```bash
# 查看变更状态
python scripts/git_automation.py --status

# 每日自动提交
python scripts/git_automation.py --daily

# 生成更新日志
python scripts/git_automation.py --changelog
```

## 定时任务（每日23:00）

```bash
# 配置定时任务
python scripts/task_scheduler.py --setup

# 查看状态
python scripts/task_scheduler.py --status

# 删除定时任务
python scripts/task_scheduler.py --remove
```

## 文件结构

```
self-evolver/
├── SKILL.md              # 本文档
├── scripts/
│   ├── main.py           # 主入口
│   ├── usage_tracker.py  # 使用追踪（自动集成）
│   ├── health_checker.py # 健康检查
│   ├── report_generator.py # 复盘报告
│   ├── html_report.py    # HTML 可视化仪表盘
│   ├── auto_updater.py   # 自动更新
│   ├── skills_optimizer.py # 技能联动优化
│   ├── git_automation.py # Git 自动化
│   ├── daily_routine.py  # 每日例行程序
│   └── task_scheduler.py # 定时任务配置
├── data/
│   ├── usage_log.json    # 调用日志
│   └── metrics.json      # 聚合指标
└── reports/              # 报告输出
    ├── weekly_*.json
    └── daily_*.html
```

## 输出示例

### HTML 可视化报告
- 深色主题仪表盘
- 关键指标卡片（总调用、成功数、成功率）
- 技能排行榜
- 每日趋势图表
- 最近日志列表

### 每日例行程序输出
```
============================================================
Skills 每日例行程序
开始时间: 2026-02-02 23:00:00
============================================================

[1/6] 初始化...
[OK]

[2/6] 健康检查...
=== Skills 健康检查报告 ===
...

[3/6] 自动修复...
[OK] 应用 5 个修复

[4/6] 生成复盘报告...
[OK] 报告已保存

[5/6] 生成 HTML 可视化报告...
[OK] 报告已保存

[6/6] Git 提交...
[OK] 提交成功

============================================================
每日例行程序完成!
耗时: 12.34 秒
成功率: 97.5%
============================================================
```
