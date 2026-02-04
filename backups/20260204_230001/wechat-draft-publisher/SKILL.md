---
name: wechat-draft-publisher
description: 自动将 HTML 文章发布到微信公众号草稿箱。支持封面图上传、标题、作者和摘要管理，HTML 自动优化适配微信。当用户说"推送到微信"、"发布到公众号草稿"、"上传到草稿箱"时使用。
allowed-tools: Read, Write, Edit, Bash, Glob
---

# 微信公众号草稿发布器

## 快速开始

```bash
cd .claude/skills/wechat-draft-publisher

# 标准发布
python publisher.py --title "文章标题" --content article.html

# 完整参数
python publisher.py \
  --title "标题" \
  --content article.html \
  --author "作者" \
  --cover cover.png \
  --digest "摘要"
```

## 工作流程

1. 查找 HTML 文件（优先 `*_formatted.html`）
2. 提取文章标题（从注释、文件名或询问用户）
3. 检查封面图（查找 `cover.png`）
4. 调用发布脚本
5. 验证结果，获取 media_id
6. 提示用户后续操作

## 配置要求

首次运行会自动引导配置：
1. 访问 https://mp.weixin.qq.com → 设置 → 基本配置
2. 复制 AppID 和 AppSecret
3. 运行发布器，按提示配置

配置文件：`~/.wechat-publisher/config.json`

## 核心功能

- access_token 自动缓存（7200秒）
- 封面图上传
- HTML 自动优化适配微信
- 字段长度自动截断
- 错误处理和中文提示
- 交互模式和命令行模式

## 错误码

参见 [error-codes.md](references/error-codes.md)

## 详细指南

| 主题 | 参考 |
|------|------|
| HTML 处理 | [scripts/fix-wechat-style.py](scripts/fix-wechat-style.py) |
| 安装配置 | [scripts/install.sh](scripts/install.sh) |
| 错误码 | [error-codes.md](references/error-codes.md) |

## 质量检查清单

- [ ] 标题 ≤64 字符
- [ ] 作者 ≤20 字节
- [ ] 摘要 ≤120 字节
- [ ] 封面图存在且 <2MB
- [ ] HTML 内容非空
- [ ] access_token 有效
- [ ] 草稿创建成功，获取 media_id
