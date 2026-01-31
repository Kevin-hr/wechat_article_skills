---
name: wechat-draft-verifier
description: 验证微信公众号草稿发布结果。检查草稿是否成功创建、标题作者是否正确、日志记录是否完整。当用户说"验证草稿"、"检查发布结果"、"确认发布"时使用。
allowed-tools: Read, Write, Bash, Glob
---

# 微信公众号草稿验证工具

## 快速开始

```bash
cd C:/Users/52648/Documents/GitHub/wechat_article_skills

# 验证所有草稿
python scripts/verify_drafts.py

# 查看详细日志
type logs/verify.log
```

## 功能

1. **检查发布状态**
   - 验证草稿是否成功创建
   - 检查 media_id 是否生成
   - 确认标题和作者信息

2. **日志管理**
   - 自动记录发布历史
   - 日志位置：`logs/verify.log`
   - 包含时间戳、标题、作者、media_id

3. **问题排查**
   - 检查 token 缓存状态
   - 验证配置文件存在性
   - 提供错误解决方案

## 输出示例

```
✓ 草稿验证完成
  - 最近发布：2026-01-31 14:30:00
  - 标题：xxx
  - 作者：YanG
  - media_id：xxx
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
✓ 草稿验证完成
```

## 质量检查清单

验证前检查：
- [ ] publisher.py 已成功运行
- [ ] media_id 已生成
- [ ] 日志文件可访问
- [ ] 配置文件存在
