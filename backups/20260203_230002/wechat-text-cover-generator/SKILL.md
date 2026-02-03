---
name: wechat-text-cover-generator
description: 使用本地 Pillow 库将文字转换为图片封面，无需 API 调用。支持多种主题配色，适合微信公众号封面生成。当用户说"生成封面"、"创建封面图片"、"文字转图片"时使用。
allowed-tools: Read, Write, Bash
---

# 本地文字转封面图片工具

## 快速开始

```bash
cd C:/Users/52648/Documents/GitHub/wechat_article_skills

# 基本用法
python scripts/create_text_cover.py --title "标题" --output cover.png

# 指定主题
python scripts/create_text_cover.py --title "标题" --output cover.png --theme blue

# 带副标题
python scripts/create_text_cover.py --title "标题" --subtitle "副标题" --output cover.png --theme green
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --title | 标题（必需） | - |
| --subtitle | 副标题 | 空 |
| --output | 输出文件路径（必需） | - |
| --theme | 主题：blue/green/dark | blue |
| --width | 图片宽度 | 900 |
| --height | 图片高度 | 383 |

## 主题配色

| 主题 | 背景色 | 文字色 | 强调色 |
|------|--------|--------|--------|
| blue | #1A1F5C | 白色 | 青色 #00FFFF |
| green | #10B981 | 白色 | 黄色 #FFE600 |
| dark | #1E1E1E | 白色 | 红色 #FF6464 |

## 特点

- ✅ **本地运行**：无需 API 调用，稳定可靠
- ✅ **无需翻墙**：不依赖外部服务
- ✅ **支持中文**：自动查找系统字体（msyh.ttc/simhei.ttf）
- ✅ **快速生成**：秒级完成

## 使用场景

1. **AI 写作技能无法调用 Gemini API 时**（代理问题）
2. **网络不稳定**需要本地备用方案
3. **简单封面需求**不需要复杂设计

## 推荐尺寸

- 微信公众号封面：900x500px（2:1 比例）
- 本工具默认：900x383px（约 2.35:1）

## 输出示例

```
✅ 封面生成成功！
📄 输出文件: cover.png
📐 尺寸: 900x383px
🎨 主题: blue
```

## 质量检查清单

生成前检查：
- [ ] 标题文字简洁明确
- [ ] 副标题辅助说明（按需）
- [ ] 选择合适的主题配色
- [ ] 输出文件路径正确
