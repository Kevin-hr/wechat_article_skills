# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

微信文章工具箱 - 一站式微信公众号文章工具集，包含：
- **AI 写作 Agent**：技术视角（wechat-tech-writer）、产品经理视角（wechat-product-manager-writer）
- **文章格式化器**：Markdown 转微信优化 HTML，支持三种主题
- **草稿发布器**：通过微信 API 自动发布草稿
- **封面生成器**：本地文字转图片封面

## 常用命令

```bash
# 安装依赖（文章格式化器）
pip install markdown beautifulsoup4 cssutils lxml pygments

# 生成封面（本地 Pillow，推荐）
python scripts/create_text_cover.py --title "标题" --output cover.png --theme blue

# Markdown 转 HTML
python wechat-article-formatter/scripts/markdown_to_html.py --input article.md --output article.html --theme tech

# 发布到微信草稿箱
python wechat-draft-publisher/publisher.py --title "标题" --content article.html --cover cover.png --author "作者"

# 验证发布结果
python scripts/verify_drafts.py
```

## 核心组件

| 组件 | 文件 | 说明 |
|------|------|------|
| 文章格式化器 | `wechat-article-formatter/scripts/markdown_to_html.py` | `WeChatHTMLConverter` 类，输出内联 CSS |
| 草稿发布器 | `wechat-draft-publisher/publisher.py` | `WeChatPublisher` 类，token 缓存 7200 秒 |
| 封面生成 | `scripts/create_text_cover.py` | 本地 Pillow 生成，稳定可靠 |
| 草稿验证 | `scripts/verify_drafts.py` | 检查发布结果，日志在 `logs/verify.log` |

## 主题

- `tech` - 科技风（蓝紫渐变）
- `minimal` - 简约风（黑白灰）
- `business` - 商务风（深蓝金）

## 微信编辑器兼容性

自动修复：
- `div`/`section` 带背景色 → `table`
- CSS 注入 `!important`
- HTML 压缩（去除空白符）
- 移除不支持的 CSS：`box-shadow`、`text-shadow`、`gradients`

## 配置

创建 `~/.wechat-publisher/config.json`：
```json
{
  "appid": "wx1234567890abcdef",
  "appsecret": "你的应用密钥"
}
```
- 需在微信公众平台配置 IP 白名单

## 错误码

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 40164 | IP 不在白名单 | 微信后台添加 IP |
| 40001 | 凭证无效 | 检查 config.json |
| 42001 | 令牌过期 | 删除 token_cache.json |
| 45009 | API 频率限制 | 等待次日 |

## AI 写作 Agent

写作技能已升级为 **Agent 模式**，具备自主决策能力。

| Agent | 定位 | 触发词 |
|-------|------|--------|
| wechat-tech-writer | 技术科普文章，自动研究并撰写 | "写一篇关于XXX"、"帮我研究XXX" |
| wechat-product-manager-writer | 产品经理视角，观点鲜明 | "分析XXX产品"、"聊聊XXX" |

### wechat-product-manager-writer
- **5 种内容类型**：AI 产品拆解、场景解决方案、效率提升实战、产品方法论、行业观察
- **强制要求**：封面图 + 内容结构图
- **写作风格**：第一人称、实战导向、观点鲜明

### wechat-tech-writer
- **3 种文章类型**：新闻资讯、介绍类、概念科普
- **自主策略**：根据内容自动选择搜索策略、写作框架、配图方案

### Gemini 生图代理设置

调用 Gemini API 时必须清空代理：
```bash
cd /root/.claude/skills/wechat-tech-writer  # 或 wechat-product-manager-writer
ALL_PROXY="" all_proxy="" python scripts/generate_image.py --prompt "..." --api gemini --output cover.png
```

### Agent vs Skill 区别

| 维度 | Skill | Agent |
|------|-------|-------|
| 决策 | 按固定流程执行 | 自主判断动态调整 |
| 搜索 | 固定轮次 | 按需迭代补充 |
| 框架 | 预设结构 | 根据类型选择 |
| 文件 | `.claude/skills/*/SKILL.md` | `.claude/agents/*.agent` |

## 重要约定

- 文件编码：UTF-8
- 链接格式：纯文本 URL（不用 Markdown 链接）
- H1：从 HTML 正文中移除
- 默认作者：「雲帆AI」
- 标题 ≤64 字符，作者 ≤20 字节，摘要 ≤120 字节
- 封面推荐 900x500px，<2MB

## 文档

- `docs/COMPLETE_WORKFLOW.md` - 完整发布流程
- `.claude/agents/wechat-tech-writer.agent` - 技术写作 Agent
- `.claude/agents/wechat-product-manager-writer.agent` - 产品经理写作 Agent
