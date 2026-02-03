---
name: wechat-draft-verifier
description: 验证微信公众号草稿发布结果。检查草稿是否成功创建、标题作者是否正确、日志记录是否完整。当用户说"验证草稿"、"检查发布结果"、"确认发布"时使用。
allowed-tools: Read, Write, Bash, Glob
---

# 微信公众号草稿验证工具

## 快速开始

```bash
cd C:/Users/52648/Documents/GitHub/wechat_article_skills
python scripts/verify_drafts.py
```

## 脚本参数

| 参数 | 说明 |
|------|------|
| 无参数 | 验证所有草稿，显示最近5条 |
| `--json` | JSON 格式输出 |
| `--limit N` | 显示最近 N 条 |

## 功能

1. **检查发布状态** - 验证草稿是否成功创建、media_id 是否生成、标题作者是否正确
2. **日志管理** - 自动记录到 `logs/verify.log`，包含时间戳、标题、作者、media_id
3. **问题排查** - 检查 token 缓存、配置文件，提供错误解决方案

## 输出示例

```
=== Verifying Drafts in WeChat Official Account ===
Total drafts found: 5
--------------------------------------------------
Title:   OpenClaw 高质量技能推荐
Author:  雲帆AI
Time:    2026-02-01 01:31:06
CoverID: 4Gr49llTYrmr-iwGtmaC3-...
Digest:  OpenClaw 高质量技能推荐...
--------------------------------------------------
[OK] 草稿验证完成
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `logs/verify.log` | 发布历史日志 |
| `~/.wechat-publisher/config.json` | 配置文件 |
| `~/.wechat-publisher/token_cache.json` | Token 缓存 |

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 草稿未找到 | 检查是否成功调用 publisher.py |
| 日志为空 | 确认 publisher.py 有写入权限 |
| token 过期 | 删除 token_cache.json 重新获取 |
