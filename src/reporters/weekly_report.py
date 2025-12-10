"""
Weekly report generator
Creates comprehensive weekly reports of LP investment activity
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

from ..database.models import NewsItem
from ..database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class WeeklyReportGenerator:
    """Generates weekly LP monitoring reports"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize report generator"""
        self.db = db_manager

    def generate_report(
        self,
        start_date: str = None,
        end_date: str = None,
        output_format: str = "markdown"
    ) -> str:
        """Generate weekly report"""
        # Calculate date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        if not start_date:
            start = datetime.now() - timedelta(days=7)
            start_date = start.strftime('%Y-%m-%d')

        logger.info(f"Generating weekly report for {start_date} to {end_date}")

        # Fetch news items
        news_items = self.db.get_news_by_date_range(start_date, end_date)

        if output_format == "markdown":
            return self._generate_markdown_report(news_items, start_date, end_date)
        elif output_format == "html":
            return self._generate_html_report(news_items, start_date, end_date)
        else:
            return self._generate_markdown_report(news_items, start_date, end_date)

    def _generate_markdown_report(
        self,
        news_items: List[NewsItem],
        start_date: str,
        end_date: str
    ) -> str:
        """Generate markdown format report"""
        # Sort by relevance score and date
        high_relevance = [n for n in news_items if n.korea_relevance_score >= 4]
        high_relevance.sort(key=lambda x: (x.korea_relevance_score, x.date), reverse=True)

        # Group by LP
        by_lp = {}
        for news in news_items:
            if news.lp_name not in by_lp:
                by_lp[news.lp_name] = []
            by_lp[news.lp_name].append(news)

        # Group by category
        by_category = {}
        for news in news_items:
            if news.category:
                if news.category not in by_category:
                    by_category[news.category] = []
                by_category[news.category].append(news)

        # Calculate statistics
        total_commitments = sum(
            news.amount for news in news_items
            if news.amount and news.category == '신규_출자_약정'
        ) or 0

        # Build report
        report = f"""# LP 투자 동향 주간 리포트
**기간**: {start_date} ~ {end_date}
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📌 이번 주 핵심 요약

- **총 뉴스 수**: {len(news_items)}개
- **한국 관련 고득점 시그널**: {len(high_relevance)}개
- **신규 커밋먼트 총액**: ${total_commitments:,.0f}
- **활동 LP 수**: {len(by_lp)}개

"""

        # Executive summary (top insights)
        if high_relevance:
            report += "### 🔍 주요 인사이트\n\n"
            insights = self._generate_insights(news_items, by_lp, by_category)
            for i, insight in enumerate(insights, 1):
                report += f"{i}. {insight}\n"
            report += "\n"

        # High relevance news
        if high_relevance:
            report += "## 🔥 한국 VC 주목 시그널 (스코어 4-5)\n\n"

            for news in high_relevance[:10]:  # Top 10
                stars = "⭐" * news.korea_relevance_score
                report += f"### {news.lp_name} - {news.title} {stars}\n\n"

                if news.content_summary:
                    report += f"{news.content_summary}\n\n"

                report += f"- **날짜**: {news.date}\n"
                report += f"- **카테고리**: {news.category}\n"

                if news.amount:
                    report += f"- **금액**: ${news.amount:,.0f}\n"

                if news.sectors:
                    report += f"- **섹터**: {', '.join(news.sectors)}\n"

                if news.key_points:
                    report += "\n**주요 포인트:**\n"
                    for point in news.key_points:
                        report += f"- {point}\n"

                if news.action_items:
                    report += "\n**액션 아이템:**\n"
                    for item in news.action_items:
                        report += f"- {item}\n"

                report += f"\n[원문 보기]({news.url})\n\n---\n\n"

        # New commitments
        commitments = [
            n for n in news_items
            if n.category == '신규_출자_약정' and n.amount
        ]
        if commitments:
            commitments.sort(key=lambda x: x.amount, reverse=True)

            report += "## 📊 신규 커밋먼트 현황\n\n"
            report += "| LP | 금액 (USD) | 섹터 | 날짜 |\n"
            report += "|---|---|---|---|\n"

            for news in commitments[:15]:
                sectors = ', '.join(news.sectors[:3]) if news.sectors else '-'
                report += f"| {news.lp_name} | ${news.amount:,.0f} | {sectors} | {news.date} |\n"

            report += "\n"

        # News by LP
        report += "## 📰 LP별 활동 요약\n\n"
        for lp_name in sorted(by_lp.keys()):
            news_list = by_lp[lp_name]
            high_score_count = sum(1 for n in news_list if n.korea_relevance_score >= 4)

            report += f"### {lp_name}\n"
            report += f"- 뉴스 수: {len(news_list)}개"

            if high_score_count > 0:
                report += f" (🔥 고득점: {high_score_count}개)"

            report += "\n\n"

            # List top 3 news for this LP
            sorted_news = sorted(
                news_list,
                key=lambda x: x.korea_relevance_score,
                reverse=True
            )
            for news in sorted_news[:3]:
                score_indicator = "🔥" if news.korea_relevance_score >= 4 else "•"
                report += f"{score_indicator} [{news.title}]({news.url}) ({news.date})\n"

            report += "\n"

        # Category breakdown
        if by_category:
            report += "## 📂 카테고리별 분류\n\n"
            for category in sorted(by_category.keys()):
                count = len(by_category[category])
                report += f"- **{category}**: {count}개\n"
            report += "\n"

        # Market trends
        report += "## 💡 시사점 및 액션 아이템\n\n"
        action_items = self._generate_action_items(news_items, high_relevance)
        for item in action_items:
            report += f"- {item}\n"

        report += "\n---\n\n"
        report += f"*본 리포트는 자동 생성되었습니다. ({datetime.now().strftime('%Y-%m-%d %H:%M')})*\n"

        return report

    def _generate_insights(
        self,
        news_items: List[NewsItem],
        by_lp: Dict,
        by_category: Dict
    ) -> List[str]:
        """Generate key insights from news"""
        insights = []

        # Most active LP
        if by_lp:
            most_active = max(by_lp.items(), key=lambda x: len(x[1]))
            insights.append(
                f"{most_active[0]}가 {len(most_active[1])}건의 뉴스로 가장 활발한 활동 보임"
            )

        # Large commitments
        large_commitments = [
            n for n in news_items
            if n.amount and n.amount >= 500_000_000
        ]
        if large_commitments:
            insights.append(
                f"대형 커밋먼트 ($500M 이상) {len(large_commitments)}건 발생"
            )

        # Korea-related
        korea_news = [n for n in news_items if n.korea_relevance_score >= 4]
        if korea_news:
            korea_lps = set(n.lp_name for n in korea_news)
            insights.append(
                f"{len(korea_lps)}개 LP에서 한국 관련 고득점 시그널 {len(korea_news)}건"
            )

        # Sector trends
        all_sectors = []
        for news in news_items:
            all_sectors.extend(news.sectors)

        if all_sectors:
            from collections import Counter
            sector_counts = Counter(all_sectors)
            top_sector = sector_counts.most_common(1)[0]
            insights.append(
                f"{top_sector[0]} 섹터가 {top_sector[1]}건으로 가장 많이 언급됨"
            )

        return insights

    def _generate_action_items(
        self,
        news_items: List[NewsItem],
        high_relevance: List[NewsItem]
    ) -> List[str]:
        """Generate actionable items"""
        actions = []

        if high_relevance:
            actions.append(
                f"한국 관련 고득점 시그널 {len(high_relevance)}건에 대해 심층 분석 필요"
            )

            # Specific LPs to contact
            lps_to_contact = list(set(n.lp_name for n in high_relevance))
            if lps_to_contact:
                actions.append(
                    f"다음 LP들과의 접촉 고려: {', '.join(lps_to_contact[:5])}"
                )

        # Sector opportunities
        all_sectors = []
        for news in high_relevance:
            all_sectors.extend(news.sectors)

        if all_sectors:
            unique_sectors = list(set(all_sectors))
            actions.append(
                f"주목 섹터: {', '.join(unique_sectors[:5])} - 포트폴리오 매칭 검토"
            )

        # Default action
        if not actions:
            actions.append("금주 특이사항 없음. 정기 모니터링 지속")

        return actions

    def _generate_html_report(
        self,
        news_items: List[NewsItem],
        start_date: str,
        end_date: str
    ) -> str:
        """Generate HTML format report"""
        # Convert markdown to HTML (basic)
        markdown_report = self._generate_markdown_report(news_items, start_date, end_date)

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LP 투자 동향 주간 리포트 - {start_date} ~ {end_date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .high-score {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <pre>{markdown_report}</pre>
    </div>
</body>
</html>"""

        return html

    def save_report(
        self,
        report: str,
        filename: str = None,
        output_dir: str = "reports/weekly"
    ) -> str:
        """Save report to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"weekly_report_{timestamp}.md"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Report saved to: {filepath}")
        return str(filepath)
