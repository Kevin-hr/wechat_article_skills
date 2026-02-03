# 微信公众号文章工具集 | WeChat Article Skills

## 项目简介

一套强大的微信公众号文章工具集，涵盖 **AI 写作**、**爆款封面生成**、**文章格式化** 和 **草稿发布** 四大核心功能。支持 Claude Code Skills 集成，助你高效创作、美化和发布微信公众号文章。

## 核心工具

### 微信文章专用

| 功能 | 工具 | 说明 |
|------|------|------|
| **AI 爆款写作** | wechat-viral-content-writer | 活人感+HKR原则，雲帆AI原创方法论 |
| **技术写作** | wechat-tech-writer | 自动研究+撰写技术科普文章 |
| **产品写作** | wechat-product-manager-writer | 产品经理视角，6 种内容类型 |
| **爆款封面** | wechat-viral-cover | 6 种爆款封面类型，AI 生图 |
| **文字封面** | wechat-text-cover-generator | 本地 Pillow 文字转图片 |
| **文章美化** | wechat-article-formatter | Markdown → 微信优化 HTML，3 种主题 |
| **草稿发布** | wechat-draft-publisher | 自动推送到微信草稿箱 |
| **草稿验证** | wechat-draft-verifier | 检查发布结果 |
| **图像识别** | wechat-image-recognizer | 多模型 OCR/内容分析 |
| **ComfyUI** | wechat-comfyui-image-generator | 微信版 ComfyUI 生图 |

### 通用型 Skills

| 功能 | 工具 | 说明 |
|------|------|------|
| **配图助手** | image-assistant | 文章→信息图提示词 |
| **PRD 写作** | prd-doc-writer | 需求文档 Story 驱动撰写 |
| **项目推广** | project-amplifier | 病毒式传播内容（公众号/短视频） |
| **需求变更** | req-change-workflow | 标准化需求变更流程 |
| **思维挖掘** | thought-mining | 从想法到文章完整流程 |
| **Skill 创建** | skill-creator | 创建新 Skill 指南 |
| **ComfyUI** | comfyui-image-generator | 通用 ComfyUI 工作流管理 |

## 快速开始

### 安装依赖

```bash
pip install markdown beautifulsoup4 cssutils lxml pygments pillow requests
```

### 典型工作流程

**全流程一句话搞定**
```
帮我写一篇关于 Claude Code 的文章，美化后推送到微信
```

**分步骤**
1. 使用 AI 写作 Agent 生成内容
2. 生成爆款封面
3. 美化排版
4. 发布到微信草稿箱
5. 验证发布结果

## 项目结构

```
wechat_article_skills/
├── .claude/
│   ├── agents/              # Agent 配置文件
│   │   ├── wechat-viral-content-writer.agent
│   │   ├── wechat-comfyui-image-generator.agent
│   │   ├── wechat-product-manager-writer.agent
│   │   └── wechat-tech-writer.agent
│   ├── skills/              # Skill 工具
│   │   ├── wechat-viral-cover/       # 爆款封面
│   │   ├── wechat-article-formatter/  # 文章美化
│   │   ├── wechat-draft-publisher/    # 草稿发布
│   │   ├── wechat-draft-verifier/     # 草稿验证
│   │   ├── wechat-tech-writer/        # 技术写作
│   │   ├── wechat-product-manager-writer/  # 产品写作
│   │   ├── wechat-image-recognizer/   # 图像识别
│   │   ├── wechat-text-cover-generator/  # 文字封面
│   │   ├── wechat-comfyui-image-generator/  # ComfyUI
│   │   ├── image-assistant/           # 配图助手
│   │   ├── prd-doc-writer/            # PRD 写作
│   │   ├── project-amplifier/         # 项目推广
│   │   ├── req-change-workflow/       # 需求变更
│   │   ├── thought-mining/            # 思维挖掘
│   │   ├── skill-creator/             # Skill 创建
│   │   ├── comfyui-image-generator/   # ComfyUI
│   │   └── self-evolver/              # 自我进化
│   └── knowledge/            # 知识管理
├── articles/                 # 示例文章
├── scripts/                  # 实用脚本
└── docs/                     # 文档
```

## 使用场景

### 技术博客作者
- 使用 AI 写作助手生成技术内容
- 使用 tech 主题美化排版
- 一键发布到公众号

### 内容运营者
- 批量转换历史文章
- 多主题适配不同风格
- 自动化发布流程

### 自媒体创作者
- Markdown 专注写作
- 一键转换精美排版
- 快速发布到公众号

## 系统要求

- **Python**: 3.6+
- **操作系统**: Windows / macOS / Linux
- **微信公众号**: 认证的服务号或订阅号（用于 API 发布）

## 配置说明

### 草稿发布配置

创建配置文件 `~/.wechat-publisher/config.json`：

```json
{
  "appid": "your_appid",
  "appsecret": "your_appsecret"
}
```

**获取 AppID 和 AppSecret：**
1. 登录[微信公众平台](https://mp.weixin.qq.com)
2. 进入"设置与开发" → "基本配置"
3. 查看开发者 ID 和密码

## 文档资源

- [完整发布流程](./docs/COMPLETE_WORKFLOW.md)
- 各工具详细文档见 `.claude/skills/*/SKILL.md`

## 注意事项

1. **API 调用限制**
   - access_token 每日获取次数有限（2000次/天）
   - 工具自动缓存 token

2. **图片使用规范**
   - 封面图片建议尺寸：900x500 像素
   - 图片大小不超过 2MB

3. **样式兼容性**
   - 微信编辑器对 CSS 支持有限
   - 建议使用工具提供的标准主题

## 常见问题

**Q: 粘贴后样式丢失？**
- 使用 Chrome 或 Edge 浏览器
- 尝试全选复制

**Q: access_token 获取失败？**
- 检查 AppID 和 AppSecret
- 确认公众号已认证
- 检查 IP 白名单配置

## 许可证

MIT License - 供个人和商业使用

## 致谢

感谢以下开源项目：
- [Python-Markdown](https://python-markdown.github.io/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://requests.readthedocs.io/)
