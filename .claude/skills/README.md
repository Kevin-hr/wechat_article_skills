# WeChat Article Skills 打包配置

## 包含的 Skills

| Skill | 功能 | 触发词 |
|-------|------|--------|
| wechat-article-formatter | Markdown转HTML | "美化文章"、"格式化" |
| wechat-draft-publisher | 草稿发布 | "推送到微信"、"发布" |
| wechat-tech-writer | 技术文章生成 | "写技术文章" |
| image-assistant | 配图提示词 | "生成配图"、"信息图" |
| prd-doc-writer | PRD文档 | "写PRD"、"需求文档" |
| req-change-workflow | 需求变更 | "改需求"、"需求变更" |

## 公共依赖

```txt
markdown
beautifulsoup4
cssutils
lxml
pygments
pillow
requests
```

## 使用方式

```bash
# 安装依赖
pip install -r requirements.txt

# 使用 skill
cd .claude/skills/{skill-name}
python scripts/xxx.py
```
