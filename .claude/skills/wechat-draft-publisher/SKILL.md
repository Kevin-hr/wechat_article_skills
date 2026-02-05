---
name: wechat-draft-publisher
description: 将HTML文章发布到微信公众号草稿箱，支持封面图、标题、作者、摘要管理。遇到"推送到微信"、"发布到公众号"、"上传草稿"时使用。
allowed-tools: Read, Write, Edit, Bash, Glob
---

# 微信公众号草稿发布器

## 快速开始

```bash
cd .claude/skills/wechat-draft-publisher
python publisher.py --title "文章标题" --content article.html
```

## 完整参数

```bash
python publisher.py \
  --title "标题" \
  --content article.html \
  --author "作者" \
  --cover cover.png \
  --digest "摘要"
```

## 工作流程

1. 查找 HTML 文件
2. 提取标题和作者
3. 上传封面图
4. 调用微信 API 创建草稿
5. 返回 media_id

## 限制检查

- 标题: ≤64字符
- 作者: ≤20字节
- 摘要: ≤120字节
- 封面: <2MB

## 配置

首次运行引导配置:
```bash
python publisher.py --setup
```

配置文件: `~/.wechat-publisher/config.json`
