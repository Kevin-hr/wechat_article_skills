---
name: wechat-article-formatter
description: 将Markdown文章转换为美化的HTML格式，适配微信公众号发布。支持多种精美主题模板。当用户说"美化这篇文章"、"转换为HTML"、"优化公众号格式"时使用。
allowed-tools: Read, Write, Edit, Bash, Glob
---

# 微信公众号文章格式化工具

## 快速开始

```bash
cd .claude/skills/wechat-article-formatter
python scripts/markdown_to_html.py --input article.md --theme tech --preview
```

## 模板选择

**精美模板** (examples/):
- VSCode 蓝色科技风
- 红蓝对决·深度测评
- 极客暗黑风
- 现代极简风
- 高端商务·黑金咨询风

**基础主题** (templates/):
- tech - 技术文章
- minimal - 纯文字
- business - 商业报告

## 转换步骤

1. 获取输入 Markdown 文件
2. 选择模板或主题
3. 执行转换: `python scripts/markdown_to_html.py`
4. 代码块转换: `python scripts/convert-code-blocks.py`

## 输出

- `{name}_formatted.html` - 格式化后的HTML
- 代码块已适配微信显示
