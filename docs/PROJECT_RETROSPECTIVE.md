# 项目复盘与经验归档 (Project Retrospective)

## 🎯 核心目标
构建一套自动化、高可靠的微信公众号文章发布工作流，从内容生成到排版、封面制作、最终发布，全程脚本化。

## ⚠️ 遇到的关键挑战与解决方案

### 1. 封面配图事故 (The Cover Image Incident)
*   **问题**：依赖外部 API 生成封面失败时，系统自动使用了默认的兜底图片（Meta收购Manus），导致两篇新文章（关于AI和职业规划）配图严重文不对题。
*   **教训**：**绝不信任不透明的兜底逻辑**。如果核心资源（如封面）生成失败，流程应该报错暂停，或者使用**内容相关**的兜底方案。
*   **解决方案**：
    *   开发 `scripts/create_text_cover.py`，在 API 不可用时，根据**文章标题**自动生成极简风格的文字封面。
    *   **原则**：丑一点的文字图（内容相关） > 精美的无关图（严重错误）。

### 2. 微信接口安全限制 (Security Restrictions)
*   **问题**：频繁遇到 `40164 invalid ip` 错误。
*   **陷阱**：本机通过 `ipconfig` 看到的通常是内网 IP，而微信服务器看到的是公网出口 IP。
*   **解决方案**：
    *   不要猜 IP。直接运行脚本，看微信返回的报错信息中的 `hint: [IP]`，那个才是准确的。
    *   必须在公众号后台手动添加该 IP 到白名单。

### 3. Token 缓存陷阱 (Token Caching)
*   **问题**：修改了 AppID/Secret 后，脚本依然报错 `40001`。
*   **原因**：发布脚本为了性能，会缓存 `access_token` 到本地文件。配置更新了，但脚本还在用旧 Token。
*   **解决方案**：
    *   遇到权限问题，第一反应：**删除 `~/.wechat-publisher/token_cache.json`**。
    *   强制脚本重新获取 Token。

### 4. 盲目自信 (Verification Gap)
*   **问题**：脚本显示“发布成功”，就以为万事大吉，没有人工或自动校验。
*   **解决方案**：
    *   开发 `scripts/verify_drafts.py`。
    *   **SOP (标准作业程序)**：发布命令执行后，**必须**紧接着运行验证脚本，打印出最新草稿的标题、作者和封面 ID，确保与预期一致。

## 📂 关键资产清单

| 脚本/文件 | 作用 | 备注 |
| :--- | :--- | :--- |
| `wechat-draft-publisher/publisher.py` | 核心发布器 | 负责上传图文素材 |
| `wechat-article-formatter/scripts/markdown_to_html.py` | 格式转换器 | Markdown -> 微信样式 HTML |
| `scripts/create_text_cover.py` | **保底封面生成器** | 根据标题生成图片，不依赖 AI |
| `scripts/verify_drafts.py` | **发布验证器** | 读取后台草稿数据，防止"假成功" |
| `docs/COMPLETE_WORKFLOW.md` | 操作手册 | 新人上手必读 |

## 🚀 未来优化方向
1.  **集成验证步骤**：将 `verify_drafts.py` 的逻辑直接集成到 `publisher.py` 的最后一步，发布成功后自动展示预览信息。
2.  **多账号管理**：支持 `config.json` 配置多个公众号，通过命令行参数切换。
3.  **CI/CD 集成**：将此流程接入 GitHub Actions，实现 Push Markdown 自动发布（需解决 IP 白名单变动问题）。

---
*归档时间：2026-01-26*
*归档人：最强大脑 (Cloud Sail AI)*
