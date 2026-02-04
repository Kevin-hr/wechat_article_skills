---
name: wechat-tech-writer
description: 自动搜索、抓取、改写技术内容，生成适合微信公众号的中文科普文章。涵盖AI大模型、GitHub开源工具、技术话题。当用户说"写一篇关于XXX的文章"、"帮我研究XXX"、"生成公众号文章"时使用。
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob
---

# 微信公众号技术文章写作助手

## 核心原则

1. **封面图是强制要求**：每篇文章必须生成一张主题封面图
2. **图片文字使用中文**：提示词明确要求 "text in simplified Chinese"
3. **图片数量控制**：封面图1张 + 内容配图0-2张
4. **只输出正文**：禁止添加"参考资料"、"延伸阅读"等章节
5. **链接使用纯文本格式**

## 文章类型决策树

```
用户输入
  │
  ├─ "最新"、"发布"、"更名" → 新闻资讯类 → 配图：仅封面图
  │
  ├─ AI模型/工具名称 → 介绍类
  │   ├─ AI大模型 → 配图：封面 + 性能对比图
  │   └─ 开发工具 → 配图：封面 + 架构图
  │
  └─ 技术概念 → 概念科普 → 配图：封面 + 概念对比图
```

## 工作流程

### 步骤1：搜索（3-5轮）
- 第1轮：官方信息（官方文档、GitHub）
- 第2轮：技术解析（详细介绍、教程）
- 第3轮：对比评测（vs 竞品、评测）
- 第4轮：补充验证

### 步骤2：抓取（2-5篇）
优先级：官方文档 > 技术博客 > GitHub README > 权威媒体

### 步骤3：改写创作（2000-3000字）
结构：引子 → 是什么 → 能做什么 → 为什么选择 → 如何开始 → 总结

### 步骤4：生成封面图（强制）
**必须清空代理**：
```bash
cd .claude/skills/wechat-tech-writer
ALL_PROXY="" all_proxy="" python scripts/generate_image.py --prompt "..." --api gemini --output cover.png
```

配色方案参见 [color-schemes.md](references/color-schemes.md)

### 步骤5：生成内容配图（按需，0-2张）
- 有数据对比 → 性能对比图
- 有复杂架构 → 架构示意图

### 步骤6：输出文章
```markdown
# 文章标题

![封面图](cover.png)

## 第一部分标题
正文...

## 总结
结尾...
```

## 详细指南

| 主题 | 参考 |
|------|------|
| 写作风格 | [writing-style.md](references/writing-style.md) |
| 封面图设计 | [cover-image-guide.md](references/cover-image-guide.md) |
| 配色方案 | [color-schemes.md](references/color-schemes.md) |
| 内容配图 | [content-images-guide.md](references/content-images-guide.md) |
| AI生图技术 | [ai-image-generation.md](references/ai-image-generation.md) |
| API配置 | [api-configuration.md](references/api-configuration.md) |
| 事实核查 | [fact-checking.md](references/fact-checking.md) |

## 质量检查清单

- [ ] 封面图已生成且文字为中文
- [ ] 所有链接为纯文本格式
- [ ] 字数符合类型要求
- [ ] 核心信息有权威来源支撑
- [ ] 禁止添加参考资料章节
- [ ] 标题 ≤64 字符
