# 使用追踪机制

## 数据存储

| 文件 | 说明 |
|------|------|
| `data/usage_log.json` | 详细调用日志 |
| `data/metrics.json` | 聚合指标数据 |

## 指标定义

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| total_calls | 总调用次数 | 累计 |
| success_count | 成功次数 | 累计 |
| failure_count | 失败次数 | 累计 |
| success_rate | 成功率 | success_count / total_calls |
| avg_duration | 平均耗时 | total_duration / total_calls |

## 追踪方式

### 1. 手动追踪
```bash
python scripts/main.py track --skill wechat-viral-cover --status success --duration 2.5
```

### 2. 自动追踪（集成到工作流）
```python
from usage_tracker import track_usage

track_usage("wechat-tech-writer", success=True, duration=3.2)
```

### 3. 命令行追踪
```bash
python scripts/usage_tracker.py --track wechat-article-formatter
```

## 定时任务配置

```bash
# 每天收集使用数据
0 23 * * * cd /path/to/self-evolver && python scripts/usage_tracker.py --stats --days 1
```
