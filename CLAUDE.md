# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

微信文章工具箱 - 一站式微信公众号文章工具集，包含：
- **AI 写作 Agent**：爆款内容写作、技术写作、产品写作
- **爆款封面生成器**：基于视觉冲突+情绪锚点的 6 种类型封面
- **文章格式化器**：Markdown 转微信优化 HTML，支持三种主题
- **草稿发布器**：通过微信 API 自动发布草稿

## 常用命令

```bash
# 安装依赖
pip install markdown beautifulsoup4 cssutils lxml pygments pillow requests

# 生成爆款封面
cd .claude/skills/wechat-viral-cover
python scripts/generate_cover.py --title "你的文章标题" --output cover.png --api gemini

# 生成文字封面（本地 Pillow）
python scripts/create_text_cover.py --title "标题" --output cover.png --theme blue

# Markdown 转 HTML
python .claude/skills/wechat-article-formatter/scripts/markdown_to_html.py --input article.md --output article.html --theme tech

# 发布到微信草稿箱
python .claude/skills/wechat-draft-publisher/publisher.py --title "标题" --content article.html --cover cover.png

# ComfyUI 图像生成
python .claude/skills/comfyui-image-generator/scripts/generate_image.py --workflow workflow.json --output image.png

# 图像识别分析
python .claude/skills/wechat-image-recognizer/recognize.py --image cover.png --model gpt4v

# Skills 健康检查
python .claude/skills/self-evolver/health_check.py --report

# 验证发布结果
python scripts/verify_drafts.py
```

## 核心组件

| 组件 | 文件 | 说明 |
|------|------|------|
| 爆款封面生成 | `.claude/skills/wechat-viral-cover/scripts/generate_cover.py` | 6 种爆款类型，自动判断 |
| 文章格式化器 | `.claude/skills/wechat-article-formatter/scripts/markdown_to_html.py` | `WeChatHTMLConverter` 类，输出内联 CSS |
| 草稿发布器 | `.claude/skills/wechat-draft-publisher/publisher.py` | `WeChatPublisher` 类，token 缓存 7200 秒 |
| 文字封面生成 | `.claude/skills/wechat-text-cover-generator/scripts/create_text_cover.py` | 本地 Pillow 生成 |
| ComfyUI 图像生成 | `.claude/skills/comfyui-image-generator/scripts/generate_image.py` | 工作流模板管理 |
| 图像识别 | `.claude/skills/wechat-image-recognizer/` | 多模型支持 |
| Skills 自我进化 | `.claude/skills/self-evolver/` | 使用追踪、健康检查 |

## 爆款封面 6 维度提示词

`[主体 Subject]` + `[环境 Environment]` + `[情绪/动作 Mood]` + `[光影 Lighting]` + `[构图 Composition]` + `[风格 Style]`

### 6 种封面类型

| 类型 | 适用场景 | 视觉逻辑 |
|------|----------|----------|
| 宏观恐惧 | 危机、崩盘、AI替代、大国博弈 | 巨大的力量 vs 渺小人类 |
| 认知颠覆 | 揭秘、真相、底层逻辑、黑科技 | 表象 vs 真相，撕裂感 |
| 普通人逆袭 | 搞钱、副业、阶级跨越 | 贫富对比，金色诱惑 |
| 人物传记 | 大人物、历史、伟人 | 眼神杀，沧桑质感 |
| 科技产品 | AI工具、软件、产品评测 | 科技感，蓝紫霓虹 |
| 故事共鸣 | 个人经历、情感分享、心得 | 情感连接，人性故事 |

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
  "appid": "your_appid",
  "appsecret": "your_appsecret"
}
```
- 需在微信公众平台配置 IP 白名单

## 常见错误

| 错误码 | 解决方案 |
|--------|----------|
| 40164 | 微信后台添加 IP 到白名单 |
| 42001 | 删除 token_cache.json |
| 45009 | 等待次日再调用 |

## Agent 与 Skill

### AI 写作 Agent

| Agent | 定位 | 触发词 |
|-------|------|--------|
| wechat-viral-content-writer | 爆款内容写作，活人感+HKR原则 | "写一篇XXX"、"创作XXX" |
| wechat-tech-writer | 技术科普文章，自动研究并撰写 | "写一篇关于XXX"、"帮我研究XXX" |
| wechat-product-manager-writer | 产品经理视角，观点鲜明 | "分析XXX产品"、"聊聊XXX" |

### wechat-viral-content-writer 核心方法论

- **活人感**：拒绝 AI 味，暴露脆弱，第一人称
- **真诚**：不欺骗，长期主义
- **HKR 原则**：Hook（愉悦感）、Knowledge（知识）、Resonance（共鸣）
- **故事化**：英雄之旅结构

### 用户偏好记忆

```bash
python .claude/knowledge/user_preferences.py --show     # 查看所有偏好
python .claude/knowledge/user_preferences.py --get writing_style.preferred_style
python .claude/knowledge/user_preferences.py --set writing_style.preferred_style minimal
```

### 多平台发布

```bash
python .claude/knowledge/multi_platform.py --status              # 查看平台状态
python .claude/knowledge/multi_platform.py --enable wechat       # 启用微信
python .claude/knowledge/multi_platform.py --publish --title "标题" --content "内容"  # 同步发布
```

### AI 编辑

```bash
python .claude/knowledge/ai_editor.py --proofread article.md     # 校对文章
python .claude/knowledge/ai_editor.py --seo "标题" "内容"         # SEO 分析
python .claude/knowledge/ai_editor.py --readability article.md   # 可读性分析
python .claude/knowledge/ai_editor.py --tags "标题" "内容"        # 自动标签推荐
```

### Gemini 生图代理设置

调用 Gemini API 时必须清空代理：
```bash
cd .claude/skills/wechat-viral-cover
ALL_PROXY="" all_proxy="" python scripts/generate_cover.py --title "标题" --output cover.png --api gemini
```

## 重要约定

- 文件编码：UTF-8
- 链接格式：纯文本 URL（不用 Markdown 链接）
- H1：从 HTML 正文中移除
- 标题 ≤64 字符，作者 ≤20 字节，摘要 ≤120 字节
- 封面推荐 900x500px，<2MB

## 文档

| 文件 | 说明 |
|------|------|
| `docs/COMPLETE_WORKFLOW.md` | 完整发布流程 |
| `.claude/agents/*.agent` | Agent 配置文件 |
| `.claude/skills/*/SKILL.md` | Skill 使用说明 |
| `.claude/skills/*/references/` | 参考文档目录 |
| `.claude/knowledge/*.py` | 知识管理工具 |

## 架构说明

```
.claude/
├── agents/              # Agent 配置文件（自主决策）
├── skills/              # Skill 工具（固定流程）
│   ├── wechat-viral-cover/       # 爆款封面生成
│   ├── wechat-article-formatter/  # Markdown 转 HTML
│   ├── wechat-draft-publisher/    # 草稿发布
│   ├── wechat-draft-verifier/     # 草稿验证
│   ├── wechat-tech-writer/        # 技术写作
│   ├── wechat-product-manager-writer/  # 产品写作
│   ├── wechat-image-recognizer/   # 图像识别
│   ├── wechat-text-cover-generator/  # 文字封面
│   ├── wechat-comfyui-image-generator/  # ComfyUI
│   ├── image-assistant/           # 配图助手
│   ├── prd-doc-writer/            # PRD 写作
│   ├── project-amplifier/         # 项目推广
│   ├── req-change-workflow/       # 需求变更
│   ├── thought-mining/            # 思维挖掘
│   ├── skill-creator/             # Skill 创建
│   ├── comfyui-image-generator/   # ComfyUI
│   └── self-evolver/              # Skills 自我进化
└── knowledge/          # 知识管理
    ├── user_preferences.py      # 用户偏好
    ├── multi_platform.py        # 多平台发布
    ├── team_config.py           # 团队协作
    └── ai_editor.py             # AI 编辑
```
