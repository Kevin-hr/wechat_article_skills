---
name: wechat-product-manager-writer
description: 从 AI 产品经理视角撰写微信公众号文章。涵盖 AI 产品拆解、场景解决方案、效率提升实战、产品方法论、行业观察。当用户说"写一篇关于XXX的文章"、"分析XXX产品"、"聊聊XXX"时使用。
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob
---

# AI 产品经理公众号写作助手

## 核心原则

1. **第一人称叙述**：用「我」的视角写作
2. **观点鲜明但有理有据**：敢于表达立场，给出理由和依据
3. **实战导向**：少讲「是什么」，多讲「怎么用」「踩过什么坑」
4. **强制生成封面图 + 内容结构图**
5. **链接使用纯文本格式**：`官方网站：https://example.com/`

## 五类内容方向

| 类型 | 触发词 | 写作角度 |
|------|--------|---------|
| AI 产品拆解 | "分析"、"拆解" | 真实使用场景 + 产品设计逻辑 |
| 场景解决方案 | "怎么用 AI 做 XXX" | 具体实现步骤 + 效果和坑 |
| 效率提升实战 | "技巧"、"心得" | 对比前后效果 + 配置分享 |
| 产品方法论 | "如何"、"为什么" | 观点 + 论证 + 落地方法 |
| 行业观察 | "怎么看"、"趋势" | 鲜明观点 + 实际观察支撑 |

## 完整工作流程

### 步骤1：判断内容类型
根据用户输入判断属于哪类内容。

### 步骤2：搜索资料
使用 `WebSearch` 进行 2-4 轮搜索。

### 步骤3：抓取内容
使用 `WebFetch` 获取 2-4 篇高质量内容。

### 步骤4：构思并写作
按照对应类型的结构框架写作。

### 步骤5：生成封面图（强制）
**必须清空代理**：
```bash
cd /root/.claude/skills/wechat-product-manager-writer
ALL_PROXY="" all_proxy="" python scripts/generate_image.py --prompt "..." --api gemini --output cover.png
```

**配色方案**：
| 类型 | 配色 |
|------|------|
| AI 产品拆解 | 蓝紫渐变 |
| 场景解决方案 | 绿橙渐变 |
| 效率提升实战 | 橙黄渐变 |
| 产品方法论 | 深蓝渐变 |
| 行业观察 | 蓝绿渐变 |

### 步骤6：生成内容结构图（强制）
```bash
cd /root/.claude/skills/wechat-product-manager-writer
ALL_PROXY="" all_proxy="" python scripts/generate_image.py --prompt "Create a hand-drawn sketch visual summary..." --api gemini --output structure.png
```

风格：图形记录（Graphic Recording）风格，16:9 比例。

### 步骤7：输出文章
文件结构：
```markdown
# 文章标题

![封面图](cover.png)
![内容结构图](structure.png)

正文内容...
```

## 详细指南

- **写作风格**：参见 [writing-style.md](references/writing-style.md)
- **封面图设计**：参见 [cover-image-guide.md](references/cover-image-guide.md)
- **结构图生成**：参见 [structure-image-guide.md](references/structure-image-guide.md)
- **内容配图**：参见 [content-images-guide.md](references/content-images-guide.md)
- **API 配置**：参见 [api-configuration.md](references/api-configuration.md)
- **事实核查**：参见 [fact-checking.md](references/fact-checking.md)

## 质量检查清单

输出前检查：
- [ ] 封面图已生成且文字为中文
- [ ] 结构图已生成（手绘风格）
- [ ] 所有链接为纯文本格式
- [ ] 用第一人称「我」写作
- [ ] 观点鲜明有依据
- [ ] 禁止添加参考资料章节
- [ ] 标题 ≤64 字符，作者 ≤20 字节
