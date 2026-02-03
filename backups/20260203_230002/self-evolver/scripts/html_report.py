#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skills 可视化 HTML 报告生成器
生成美观的仪表盘，展示关键指标
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import sys
sys.path.insert(0, str(Path(__file__).parent))
from usage_tracker import load_metrics, load_usage_log, init_data_dir, get_success_rate

# 目录
SELF_EVOLVER_DIR = Path(__file__).parent.parent
REPORTS_DIR = SELF_EVOLVER_DIR / "reports"


class HTMLReportGenerator:
    """HTML 可视化报告生成器"""

    def __init__(self):
        self.metrics = load_metrics()
        self.log = load_usage_log()

    def generate_daily_report(self) -> str:
        """生成每日报告"""
        cutoff = datetime.now() - timedelta(days=1)
        today_logs = [e for e in self.log if datetime.fromisoformat(e["timestamp"]) >= cutoff]

        success_rate = get_success_rate()
        sorted_skills = sorted(self.metrics.items(), key=lambda x: x[1]["total_calls"], reverse=True)

        return self._render_html({
            "title": "每日健康报告",
            "period": "最近 24 小时",
            "success_rate": success_rate,
            "total_calls": len(today_logs),
            "skills_count": len(set(e["skill"] for e in today_logs)),
            "top_skills": sorted_skills[:5],
            "all_metrics": sorted_skills,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "logs": today_logs[-20:]
        })

    def generate_weekly_report(self) -> str:
        """生成周报告"""
        cutoff = datetime.now() - timedelta(days=7)
        week_logs = [e for e in self.log if datetime.fromisoformat(e["timestamp"]) >= cutoff]

        success_rate = get_success_rate()
        sorted_skills = sorted(self.metrics.items(), key=lambda x: x[1]["total_calls"], reverse=True)

        # 计算每日趋势
        daily_counts = {}
        for e in week_logs:
            date = e["timestamp"][:10]
            if date not in daily_counts:
                daily_counts[date] = {"total": 0, "success": 0}
            daily_counts[date]["total"] += 1
            if e["success"]:
                daily_counts[date]["success"] += 1

        return self._render_html({
            "title": "周度复盘报告",
            "period": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}",
            "success_rate": success_rate,
            "total_calls": len(week_logs),
            "skills_count": len(set(e["skill"] for e in week_logs)),
            "top_skills": sorted_skills[:5],
            "all_metrics": sorted_skills,
            "daily_trends": daily_counts,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "logs": week_logs[-50:]
        })

    def generate_monthly_report(self) -> str:
        """生成月报告"""
        cutoff = datetime.now() - timedelta(days=30)
        month_logs = [e for e in self.log if datetime.fromisoformat(e["timestamp"]) >= cutoff]

        success_rate = get_success_rate()
        sorted_skills = sorted(self.metrics.items(), key=lambda x: x[1]["total_calls"], reverse=True)

        # 计算每周趋势
        weekly_counts = {}
        for e in month_logs:
            date = datetime.fromisoformat(e["timestamp"])
            week_num = date.isocalendar()[1]
            week_key = f"W{week_num}"
            if week_key not in weekly_counts:
                weekly_counts[week_key] = {"total": 0, "success": 0}
            weekly_counts[week_key]["total"] += 1
            if e["success"]:
                weekly_counts[week_key]["success"] += 1

        return self._render_html({
            "title": "月度复盘报告",
            "period": f"{(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}",
            "success_rate": success_rate,
            "total_calls": len(month_logs),
            "skills_count": len(set(e["skill"] for e in month_logs)),
            "top_skills": sorted_skills[:5],
            "all_metrics": sorted_skills,
            "weekly_trends": weekly_counts,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "logs": month_logs[-100:]
        })

    def _render_html(self, data: Dict) -> str:
        """渲染 HTML 模板"""
        success_color = "#10b981" if data["success_rate"] >= 95 else "#f59e0b" if data["success_rate"] >= 80 else "#ef4444"

        # 技能排行 HTML
        skills_html = ""
        for skill, m in data["all_metrics"]:
            rate = (m["success_count"] / m["total_calls"] * 100) if m["total_calls"] > 0 else 0
            avg = (m["total_duration"] / m["total_calls"]) if m["total_calls"] > 0 else 0
            color = "#10b981" if rate >= 95 else "#f59e0b" if rate >= 80 else "#ef4444"
            skills_html += f"""
            <div class="skill-card" onclick="showDetail('{skill}')">
                <div class="skill-name">{skill}</div>
                <div class="skill-stats">
                    <span class="stat"><b>{m['total_calls']}</b> 次</span>
                    <span class="stat rate" style="color: {color}">{rate:.1f}%</span>
                    <span class="stat">{avg:.2f}s</span>
                </div>
                <div class="progress-bar">
                    <div class="progress" style="width: {min(rate, 100)}%; background: {color}"></div>
                </div>
            </div>
            """

        # 每日趋势 HTML（如果有）
        trends_html = ""
        if "daily_trends" in data:
            dates = sorted(data["daily_trends"].keys())
            trend_data = []
            for d in dates[-7:]:
                t = data["daily_trends"][d]
                rate = (t["success"] / t["total"] * 100) if t["total"] > 0 else 0
                trend_data.append(f'{{date: "{d}", calls: {t["total"]}, rate: {rate:.1f}}}')
            trends_html = f"""
            <div class="section">
                <h3>📈 每日趋势</h3>
                <canvas id="trendChart" width="600" height="200"></canvas>
                <script>
                    const trendData = [{", ".join(trend_data)}];
                    drawTrendChart(trendData);
                </script>
            </div>
            """

        # 最近日志 HTML
        logs_html = ""
        for entry in data["logs"]:
            status_class = "success" if entry["success"] else "fail"
            status_icon = "✓" if entry["success"] else "✗"
            time_str = entry["timestamp"][:19].replace("T", " ")
            logs_html += f"""
            <div class="log-item {status_class}">
                <span class="log-status">{status_icon}</span>
                <span class="log-time">{time_str}</span>
                <span class="log-skill">{entry['skill']}</span>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} - Skills 监控</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #e0e0e0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 30px; }}
        header h1 {{ font-size: 2em; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .period {{ color: #888; margin-top: 10px; }}
        .generated {{ color: #666; font-size: 0.9em; margin-top: 5px; }}

        /* 关键指标卡片 */
        .metrics-row {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
        .metric-card {{ flex: 1; min-width: 200px; background: linear-gradient(145deg, #1e2a4a, #0f1629); border-radius: 16px; padding: 24px; text-align: center; border: 1px solid #2a3f5f; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: {success_color}; }}
        .metric-label {{ color: #888; margin-top: 8px; font-size: 0.9em; }}

        /* 成功率大卡片 */
        .success-card {{ flex: 2; min-width: 300px; background: linear-gradient(145deg, #1e3a2f, #0a1f15); border-radius: 16px; padding: 30px; text-align: center; border: 1px solid #2a5f4f; }}
        .success-value {{ font-size: 4em; font-weight: bold; color: {success_color}; }}

        /* 技能排行 */
        .section {{ background: linear-gradient(145deg, #1e2a4a, #0f1629); border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid #2a3f5f; }}
        .section h3 {{ margin-bottom: 20px; color: #00d4ff; }}
        .skill-card {{ background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; margin-bottom: 10px; cursor: pointer; transition: all 0.3s; }}
        .skill-card:hover {{ background: rgba(255,255,255,0.1); transform: translateX(5px); }}
        .skill-name {{ font-weight: bold; margin-bottom: 8px; color: #fff; }}
        .skill-stats {{ display: flex; gap: 20px; color: #888; font-size: 0.9em; }}
        .stat.rate {{ font-weight: bold; }}
        .progress-bar {{ height: 4px; background: #333; border-radius: 2px; margin-top: 10px; overflow: hidden; }}
        .progress {{ height: 100%; border-radius: 2px; transition: width 0.3s; }}

        /* 趋势图 */
        #trendChart {{ background: rgba(0,0,0,0.2); border-radius: 8px; }}

        /* 日志列表 */
        .log-item {{ display: flex; align-items: center; gap: 15px; padding: 12px; border-bottom: 1px solid #2a3f5f; }}
        .log-item:last-child {{ border-bottom: none; }}
        .log-status {{ width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8em; }}
        .log-item.success .log-status {{ background: #10b981; color: #fff; }}
        .log-item.fail .log-status {{ background: #ef4444; color: #fff; }}
        .log-time {{ color: #666; font-size: 0.85em; font-family: monospace; }}
        .log-skill {{ color: #00d4ff; }}

        /* 详情弹窗 */
        .detail-modal {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; align-items: center; justify-content: center; }}
        .detail-content {{ background: #1a1a2e; border-radius: 16px; padding: 30px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; border: 1px solid #333; }}
        .detail-close {{ float: right; cursor: pointer; font-size: 1.5em; color: #666; }}
        .detail-close:hover {{ color: #fff; }}

        /* 响应式 */
        @media (max-width: 768px) {{ .metrics-row {{ flex-direction: column; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{data['title']}</h1>
            <div class="period">{data['period']}</div>
            <div class="generated">生成时间: {data['generated_at']}</div>
        </header>

        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-value">{data['total_calls']}</div>
                <div class="metric-label">总调用次数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{data['skills_count']}</div>
                <div class="metric-label">使用技能数</div>
            </div>
            <div class="success-card">
                <div class="success-value">{data['success_rate']:.1f}%</div>
                <div class="metric-label">成功率</div>
            </div>
        </div>

        {trends_html}

        <div class="section">
            <h3>🏆 TOP 5 活跃技能</h3>
            <div class="top-skills">
                {''.join([f'''
                <div class="skill-card">
                    <div class="skill-name">{i+1}. {skill}</div>
                    <div class="skill-stats">
                        <span class="stat"><b>{m['total_calls']}</b> 次调用</span>
                        <span class="stat" style="color: #10b981">{(m['success_count']/m['total_calls']*100) if m['total_calls']>0 else 0:.1f}% 成功</span>
                        <span class="stat">{(m['total_duration']/m['total_calls']) if m['total_calls']>0 else 0:.2f}s 平均</span>
                    </div>
                </div>
                ''' for i, (skill, m) in enumerate(data['top_skills'])])}
            </div>
        </div>

        <div class="section">
            <h3>📋 所有技能状态</h3>
            <p style="color: #666; margin-bottom: 15px;">点击技能查看详情</p>
            {skills_html}
        </div>

        <div class="section">
            <h3>📝 最近日志</h3>
            <div class="log-list">
                {logs_html}
            </div>
        </div>
    </div>

    <div class="detail-modal" id="detailModal">
        <div class="detail-content">
            <span class="detail-close" onclick="closeDetail()">&times;</span>
            <div id="detailBody"></div>
        </div>
    </div>

    <script>
        function showDetail(skill) {{
            const modal = document.getElementById('detailModal');
            const body = document.getElementById('detailBody');
            body.innerHTML = '<h2>' + skill + '</h2><p>详细分析功能开发中...</p>';
            modal.style.display = 'flex';
        }}

        function closeDetail() {{
            document.getElementById('detailModal').style.display = 'none';
        }}

        function drawTrendChart(data) {{
            const canvas = document.getElementById('trendChart');
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;

            ctx.clearRect(0, 0, w, h);
            ctx.strokeStyle = '#00d4ff';
            ctx.lineWidth = 2;
            ctx.beginPath();

            const maxCalls = Math.max(...data.map(d => d.calls));
            const padding = 40;

            data.forEach((d, i) => {{
                const x = padding + (i / (data.length - 1)) * (w - 2 * padding);
                const y = h - padding - (d.calls / maxCalls) * (h - 2 * padding);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                ctx.fillStyle = '#00d4ff';
                ctx.fillRect(x - 4, y - 4, 8, 8);
            }});

            ctx.stroke();

            // 标签
            ctx.fillStyle = '#888';
            ctx.font = '12px sans-serif';
            data.forEach((d, i) => {{
                const x = padding + (i / (data.length - 1)) * (w - 2 * padding);
                ctx.fillText(d.date.slice(5), x - 20, h - 10);
            }});
        }}

        // 点击模态框外部关闭
        document.getElementById('detailModal').addEventListener('click', function(e) {{
            if (e.target === this) closeDetail();
        }});
    </script>
</body>
</html>"""
        return html

    def save_report(self, html_content: str, report_type: str = "daily") -> str:
        """保存报告"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{report_type}_{datetime.now().strftime('%Y-%m-%d')}.html"
        filepath = REPORTS_DIR / filename
        filepath.write_text(html_content, encoding="utf-8")
        return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Skills HTML 可视化报告生成器")
    parser.add_argument("--daily", action="store_true", help="生成日报")
    parser.add_argument("--weekly", action="store_true", help="生成周报")
    parser.add_argument("--monthly", action="store_true", help="生成月报")
    parser.add_argument("--save", action="store_true", help="保存到文件")

    args = parser.parse_args()

    init_data_dir()
    generator = HTMLReportGenerator()

    if args.monthly:
        html = generator.generate_monthly_report()
        report_type = "monthly"
    elif args.weekly:
        html = generator.generate_weekly_report()
        report_type = "weekly"
    else:
        html = generator.generate_daily_report()
        report_type = "daily"

    if args.save:
        filepath = generator.save_report(html, report_type)
        print(f"[OK] 报告已保存: {filepath}")
        print(f"路径: {filepath}")
    else:
        print(html)


if __name__ == "__main__":
    main()
