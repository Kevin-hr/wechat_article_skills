# WeChat Cover Generator (Minimalist Grid Style)

基于 HTML/CSS 的微信公众号封面生成器，支持"极简格栅风"设计。

## ✨ 特性

- **严格比例**：整体 3.35:1，完美适配微信公众号封面（左侧主图 + 右侧朋友圈图）。
- **响应式设计**：基于 Tailwind CSS，自适应屏幕宽度。
- **一键下载**：使用 html2canvas 支持生成高清 PNG 图片。
- **实时预览**：修改文字立即生效。
- **极简美学**：黑白配色 + 工业风装饰 + 翡翠绿点缀。

## 🚀 使用方法

### 方式 1: 直接打开 HTML

双击 `index.html` 在浏览器中打开即可使用。

### 方式 2: 使用 Python 启动本地服务

```bash
cd wechat-cover-generator
python -m http.server 8000
```
然后访问 `http://localhost:8000`

## 🎨 设计规范

- **整体比例**: 3.35 : 1
- **左侧主图**: 2.35 : 1 (70.15% 宽度)
- **右侧时间轴**: 1 : 1 (29.85% 宽度)
- **配色**: 
  - 背景: #000000 (Pure Black)
  - 文字: #FFFFFF (White)
  - 点缀: #10B981 (Emerald 500)

## 🛠️ 技术栈

- HTML5
- Tailwind CSS (CDN)
- html2canvas (CDN)
- FontAwesome (CDN)
- Google Fonts (Noto Sans SC)
