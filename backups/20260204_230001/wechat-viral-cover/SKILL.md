---
name: wechat-viral-cover
description: 爆款封面生成器。基于雲帆AI的爆款封面法则（视觉冲突+情绪锚点），支持 4 种核心类型。当用户说"生成封面"、"设计封面"、"爆款封面"时使用。
---

# 爆款封面生成器

## 核心原则

封面不是用来"解释内容"的，是用来**制造视觉冲突**和**情绪锚点**的。

## 4 类封面公式

| 类型 | 适用场景 | 视觉逻辑 |
|------|----------|----------|
| 宏观恐惧 | 危机、崩盘、AI替代 | 巨大的力量 vs 渺小人类 |
| 认知颠覆 | 揭秘、底层逻辑 | 表象 vs 真相，撕裂感 |
| 普通人逆袭 | 副业、搞钱、阶级跨越 | 贫富对比，金色诱惑 |
| 人物传记 | 大人物、历史 | 眼神杀，沧桑质感 |

详见 [cover-types.md](references/cover-types.md)

## 快速使用

```bash
cd .claude/skills/wechat-viral-cover

# 指定类型生成
python scripts/generate_cover.py --type fear --title "金融危机来了"
python scripts/generate_cover.py --type twist --title "你不知道的真相"
python scripts/generate_cover.py --type success --title "我是如何月入10万的"
python scripts/generate_cover.py --type bio --title "马斯克的秘密"

# 自动检测类型（根据标题关键词）
python scripts/generate_cover.py --title "我是如何月入10万的"
```

## 提示词 6 维度

`[主体]` + `[环境]` + `[情绪/动作]` + `[光影]` + `[构图]` + `[风格]`

修饰词库参见 [prompt-modifiers.md](references/prompt-modifiers.md)

## 禁忌

- 不要用库存图（微笑商务团队）
- 不要用平光（证件照光）
- 不要杂乱，只有一个视觉焦点
- 不要在 prompt 里加文字

## 输出

生成 900x500px 高清封面图，适配公众号列表 + 朋友圈。
