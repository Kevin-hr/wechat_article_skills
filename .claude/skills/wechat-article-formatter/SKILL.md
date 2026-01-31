---
name: wechat-article-formatter
description: 将Markdown文章转换为美化的HTML格式，适配微信公众号发布。支持三种主题（tech/minimal/business）和精美模板。当用户说"美化这篇文章"、"转换为HTML"、"优化公众号格式"时使用。
allowed-tools: Read, Write, Edit, Bash, Glob
---

# 微信公众号文章格式化工具

## 快速开始

```bash
cd /root/.claude/skills/wechat-article-formatter

# 标准转换
python scripts/markdown_to_html.py --input article.md --theme tech --preview

# 使用精美模板
# 先查看 examples/ 目录有哪些模板
ls -lh examples/
```

## 执行流程

### 步骤1：获取输入文件
- 用户提供路径 → 直接使用
- 用户粘贴内容 → 先保存为 .md 文件
- 刚使用 wechat-tech-writer → 自动查找最新 .md 文件

### 步骤2：选择模板或主题

**优先使用精美模板**（examples/ 目录）：
| 模板 | 风格 |
|------|------|
| VSCode 蓝色科技风.html | 技术文章、产品介绍 |
| 红蓝对决·深度测评模板.html | 对比评测、深度分析 |
| 极客暗黑风.html | 技术深度文章 |
| 现代极简风.html | 通用内容 |

**无合适模板时使用基础主题**：
| 主题 | 适用场景 |
|------|---------|
| tech | 技术文章、含代码块 |
| minimal | 纯文字、通用内容 |
| business | 商业报告、数据表格 |

### 步骤3：执行转换
```bash
python scripts/markdown_to_html.py --input {文件} --theme {主题} --preview
```

### 步骤4：代码块转换（关键）
使用 `scripts/convert-code-blocks.py` 转换为微信兼容格式：
```bash
python scripts/convert-code-blocks.py input.html output.html
```

## 详细指南

- **转换详细步骤**：参见 [references/conversion-guide.md](references/conversion-guide.md)
- **发布指南**：参见 [references/publishing-guide.md](references/publishing-guide.md)
- **主题自定义**：参见 [references/theme-customization.md](references/theme-customization.md)
- **微信代码块**：参见 [references/wechat-code-blocks.md](references/wechat-code-blocks.md)
- **平台限制**：参见 [references/wechat-constraints.md](references/wechat-constraints.md)

## 质量检查清单

输出前检查：
- [ ] HTML 文件生成成功
- [ ] 代码块已转换为微信兼容格式
- [ ] 图片路径正确
- [ ] 在浏览器中预览正常
- [ ] 标题和作者信息正确
