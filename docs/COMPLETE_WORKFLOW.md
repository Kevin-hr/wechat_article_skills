# 微信公众号自动化发布实战指南 (Practical Guide)

本文档记录了从环境配置到成功发布的完整流程，特别是针对 API 配置和 IP 白名单等常见问题的解决方案。

## 1. 环境准备

### 1.1 项目初始化
确保以下三个核心模块在 `skills` 目录下：
- `wechat-article-formatter`: 文章排版工具
- `wechat-draft-publisher`: 草稿发布工具
- `wechat-tech-writer` / `wechat-product-manager-writer`: AI 写作助手

### 1.2 依赖安装
```bash
pip install requests beautifulsoup4 markdown pillow
```

## 2. 关键配置 (Configuration)

### 2.1 微信公众号配置
创建配置文件 `~/.wechat-publisher/config.json` (Windows下路径为 `C:\Users\{用户名}\.wechat-publisher\config.json`)：

```json
{
  "appid": "你的微信公众号AppID",
  "appsecret": "你的微信公众号AppSecret"
}
```
> **获取方式**：登录 [微信公众平台](https://mp.weixin.qq.com) -> 设置与开发 -> 基本配置。

### 2.2 IP 白名单配置 (CRITICAL)
**这是最容易报错的步骤**。微信接口要求调用方的 IP 必须在白名单中。

1. **获取公网 IP**：
   - 方法 A：访问 [ip138.com](https://www.ip138.com)
   - 方法 B：运行发布脚本，查看报错信息 `hint: [IP地址]`
   - **注意**：不要使用 `ipconfig` 查到的内网 IP (如 `192.168.x.x`)，必须是公网出口 IP。

2. **添加白名单**：
   - 登录微信公众平台 -> 设置与开发 -> 基本配置 -> IP白名单 -> 修改。
   - 将公网 IP 加入列表。

### 2.3 封面生成配置 (两套方案)

**方案 A：使用本地脚本生成 (推荐，100% 稳定)**
无需 API Key，直接根据标题生成带文字的封面，避免图文不符。
```bash
python scripts/create_text_cover.py \
  --title "文章标题" \
  --subtitle "副标题" \
  --output cover.png \
  --theme blue  # 可选: blue, green, dark
```

**方案 B：使用生图 API (可选)**
如果需要 AI 生成的创意图，需配置 OpenAI 兼容的 API。
```bash
python wechat-tech-writer/scripts/generate_image.py \
  --prompt "提示词" \
  --api openai \
  --base-url "https://你的API地址/v1" \
  --api-key "sk-你的密钥" \
  --output cover.png
```

## 3. 完整工作流 (Workflow)

### 第一步：撰写文章
使用 Markdown 编写文章，例如 `article.md`。

### 第二步：生成封面 (强烈推荐方案 A)
```bash
python scripts/create_text_cover.py --title "文章标题" --output cover.png
```

### 第三步：格式化 (Markdown -> HTML)
```bash
python wechat-article-formatter/scripts/markdown_to_html.py \
  --input article.md \
  --output article.html \
  --theme tech  # 可选主题: tech, business, minimal
```

### 第四步：发布草稿
```bash
python wechat-draft-publisher/publisher.py \
  --title "文章标题" \
  --content article.html \
  --cover cover.png \
  --author "作者名" \
  --digest "文章摘要"
```

### 第五步：验证发布结果 (MANDATORY)
发布后必须运行验证脚本，确认标题、作者和封面 ID 是否更新。
```bash
python scripts/verify_drafts.py
```

## 4. 故障排除 (Troubleshooting)

### 🔴 Error: 40164 invalid ip
**原因**：IP 不在白名单中。
**解决**：检查报错信息中微信返回的 IP，将其添加到公众号后台白名单。

### 🔴 Error: 40001 invalid credential
**原因**：AppID 或 AppSecret 错误，或 access_token 过期且缓存未刷新。
**解决**：
1. 检查 `config.json` 是否正确。
2. 删除 `C:\Users\{用户名}\.wechat-publisher\token_cache.json` 文件，强制重新获取 token。

### 🔴 Image Generation Error (Expecting value: line 1...)
**原因**：API 地址错误或 Key 无效。
**解决**：
1. 放弃使用不稳定的外部 API。
2. **立即切换**到 `scripts/create_text_cover.py` 生成本地封面。

## 5. 最佳实践
- **封面原则**：绝不使用不明来源的默认图片。如果 API 失败，必须回退到本地文字封面生成。
- **发布验证**：每次发布后，务必使用 `verify_drafts.py` 或登录后台确认。
- **作者管理**：发布命令中明确指定 `--author` 参数，防止使用默认值。
