"""
AI 编辑模块

提供自动校对、SEO 优化、标题优化等功能。
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EditSuggestion:
    """编辑建议"""
    type: str  # grammar, style, seo, title, readability
    original: str
    suggested: str
    reason: str
    confidence: float  # 0-1


class AIEditor:
    """AI 编辑器"""

    # 敏感词列表（示例）
    SENSITIVE_WORDS = [
        "最", "第一", "国家级", "顶级", "唯一",
    ]

    # SEO 关键词密度建议
    SEO_MIN_KEYWORD_DENSITY = 0.01  # 1%
    SEO_MAX_KEYWORD_DENSITY = 0.03  # 3%

    def __init__(self, keywords: List[str] = None):
        self.keywords = keywords or []

    def proofread(self, text: str) -> List[EditSuggestion]:
        """校对文章，返回修改建议"""
        suggestions = []

        # 1. 检查敏感词
        for word in self.SENSITIVE_WORDS:
            if word in text:
                suggestions.append(EditSuggestion(
                    type="sensitive",
                    original=word,
                    suggested=f"【{word}】",
                    reason=f"'{word}' 可能是绝对化用语，建议谨慎使用",
                    confidence=0.8,
                ))

        # 2. 检查句子长度（可读性）
        sentences = re.split(r'[。！？]', text)
        for i, sent in enumerate(sentences):
            if len(sent) > 100:
                suggestions.append(EditSuggestion(
                    type="readability",
                    original=sent[:30] + "...",
                    suggested="拆分长句",
                    reason=f"第 {i+1} 句过长 ({len(sent)} 字)，建议拆分",
                    confidence=0.7,
                ))

        # 3. 检查重复词
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        for word, count in word_count.items():
            if count > 5 and len(word) > 2:
                suggestions.append(EditSuggestion(
                    type="style",
                    original=word,
                    suggested="使用同义词替换",
                    reason=f"'{word}' 出现了 {count} 次，建议使用同义词替换",
                    confidence=0.6,
                ))

        return suggestions

    def optimize_seo(self, title: str, content: str) -> Dict:
        """SEO 优化分析"""
        result = {
            "title_length": len(title),
            "title_keywords": [],
            "content_length": len(content),
            "keyword_density": {},
            "suggestions": [],
            "score": 0,
        }

        # 检查标题关键词
        for kw in self.keywords:
            if kw in title:
                result["title_keywords"].append(kw)

        # 计算关键词密度
        for kw in self.keywords:
            count = content.count(kw)
            density = count / len(content) if content else 0
            result["keyword_density"][kw] = f"{density:.2%}"

            # 建议
            if density < self.SEO_MIN_KEYWORD_DENSITY:
                result["suggestions"].append(f"关键词 '{kw}' 密度过低 ({density:.2%})，建议增加出现次数")
            elif density > self.SEO_MAX_KEYWORD_DENSITY:
                result["suggestions"].append(f"关键词 '{kw}' 密度过高 ({density:.2%})，可能被认为是关键词堆砌")

        # 标题建议
        if len(title) < 10:
            result["suggestions"].append("标题过短，建议增加关键词")
        elif len(title) > 64:
            result["suggestions"].append("标题过长，可能被截断")

        # 计算 SEO 分数
        score = 50
        if result["title_keywords"]:
            score += 20
        score += min(20, len(content) // 100)
        score -= len(result["suggestions"]) * 5
        result["score"] = min(100, max(0, score))

        return result

    def optimize_title(self, title: str, keywords: List[str] = None) -> List[EditSuggestion]:
        """标题优化"""
        suggestions = []

        # 标题长度
        if len(title) < 10:
            suggestions.append(EditSuggestion(
                type="title",
                original=title,
                suggested=title + " - 深度解析",
                reason="标题较短，建议增加描述性文字",
                confidence=0.6,
            ))

        if len(title) > 60:
            suggestions.append(EditSuggestion(
                type="title",
                original=title,
                suggested=title[:58] + "...",
                reason="标题较长，可能在部分平台被截断",
                confidence=0.8,
            ))

        # 检查标点
        if "！" in title or "？" in title:
            suggestions.append(EditSuggestion(
                type="title",
                original=title,
                suggested=title.replace("！", "！").replace("？", "？"),
                reason="标题中使用了感叹号/问号，建议使用更平和的表达",
                confidence=0.5,
            ))

        return suggestions

    def generate_summary(self, content: str, max_length: int = 120) -> str:
        """生成摘要"""
        # 简单实现：提取前两段的关键句
        paragraphs = content.split('\n\n')[:2]
        summary_parts = []

        for para in paragraphs:
            # 提取句子
            sentences = re.split(r'[。！]', para)
            for sent in sentences[:2]:
                sent = sent.strip()
                if len(sent) > 10:
                    summary_parts.append(sent)
                    if sum(len(s) for s in summary_parts) > max_length - 10:
                        break

        summary = '。'.join(summary_parts[:3])
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."

        return summary

    def check_readability(self, text: str) -> Dict:
        """可读性分析"""
        # 计算平均句子长度
        sentences = re.split(r'[。！？]', text)
        avg_sentence_length = len(text) / len(sentences) if sentences else 0

        # 计算段落数
        paragraphs = [p for p in text.split('\n\n') if len(p.strip()) > 0]
        avg_para_length = len(text) / len(paragraphs) if paragraphs else 0

        # 简单可读性评分
        if avg_sentence_length < 30 and avg_para_length < 200:
            readability = "简单"
            score = 90
        elif avg_sentence_length < 50 and avg_para_length < 400:
            readability = "中等"
            score = 70
        else:
            readability = "较难"
            score = 50

        return {
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_paragraph_length": round(avg_para_length, 1),
            "paragraph_count": len(paragraphs),
            "readability": readability,
            "score": score,
            "suggestions": [] if score > 70 else [
                "建议缩短句子长度",
                "建议增加段落分隔",
                "考虑使用更简单的词汇",
            ],
        }

    def auto_tag(self, title: str, content: str) -> List[str]:
        """自动推荐标签"""
        tags = set()

        # 基于关键词提取
        keyword_mapping = {
            "AI": ["人工智能", "大模型", "LLM", "GPT"],
            "产品": ["产品", "功能", "设计", "体验"],
            "技术": ["代码", "开发", "API", "架构"],
            "效率": ["效率", "提速", "自动化", "工作流"],
        }

        text = title + content
        for tag, keywords in keyword_mapping.items():
            for kw in keywords:
                if kw in text:
                    tags.add(tag)
                    break

        return list(tags)


def proofread_article(title: str, content: str, keywords: List[str] = None) -> Dict:
    """文章综合校对"""
    editor = AIEditor(keywords)

    return {
        "proofread": editor.proofread(content),
        "seo": editor.optimize_seo(title, content),
        "title_suggestions": editor.optimize_title(title, keywords),
        "readability": editor.check_readability(content),
        "suggested_tags": editor.auto_tag(title, content),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI 编辑工具")
    parser.add_argument("--proofread", metavar="FILE", help="校对文章文件")
    parser.add_argument("--seo", nargs=2, metavar=("TITLE", "CONTENT"), help="SEO 分析")
    parser.add_argument("--readability", metavar="FILE", help="可读性分析")
    parser.add_argument("--tags", nargs=2, metavar=("TITLE", "CONTENT"), help="自动标签")
    parser.add_argument("--summary", nargs=2, metavar=("CONTENT", "MAX"), help="生成摘要")

    args = parser.parse_args()

    editor = AIEditor()

    if args.proofread:
        with open(args.proofread, "r", encoding="utf-8") as f:
            content = f.read()
        suggestions = editor.proofread(content)
        print(f"发现 {len(suggestions)} 条建议:")
        for s in suggestions[:5]:
            print(f"  [{s.type}] {s.original} → {s.suggested}: {s.reason}")

    elif args.seo:
        result = editor.optimize_seo(args.seo[0], args.seo[1])
        print(f"SEO 评分: {result['score']}/100")
        print(f"标题关键词: {result['title_keywords']}")
        if result['suggestions']:
            print("建议:", result['suggestions'])

    elif args.readability:
        with open(args.readability, "r", encoding="utf-8") as f:
            content = f.read()
        result = editor.check_readability(content)
        print(f"可读性: {result['readability']} ({result['score']}/100)")
        print(f"平均句长: {result['avg_sentence_length']} 字")
        print(f"段落数: {result['paragraph_count']}")

    elif args.tags:
        tags = editor.auto_tag(args.tags[0], args.tags[1])
        print(f"推荐标签: {', '.join(tags)}")

    elif args.summary:
        summary = editor.generate_summary(args.summary[0], int(args.summary[1]))
        print(f"摘要: {summary}")

    else:
        parser.print_help()
