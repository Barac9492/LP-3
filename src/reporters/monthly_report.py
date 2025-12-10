"""
Monthly report generator
Creates comprehensive monthly reports with trend analysis
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from collections import Counter

from ..database.models import NewsItem
from ..database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class MonthlyReportGenerator:
    """Generates monthly LP monitoring reports"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize report generator"""
        self.db = db_manager

    def generate_report(
        self,
        month: str = None,  # Format: YYYY-MM
        output_format: str = "markdown"
    ) -> str:
        """Generate monthly report"""
        # Calculate date range
        if not month:
            now = datetime.now()
            month = now.strftime('%Y-%m')

        start_date = f"{month}-01"

        # Calculate end date (last day of month)
        year, month_num = map(int, month.split('-'))
        if month_num == 12:
            next_month = f"{year+1}-01-01"
        else:
            next_month = f"{year}-{month_num+1:02d}-01"

        end_date = (datetime.strptime(next_month, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')

        logger.info(f"Generating monthly report for {start_date} to {end_date}")

        # Fetch news items
        news_items = self.db.get_news_by_date_range(start_date, end_date)

        if output_format == "markdown":
            return self._generate_markdown_report(news_items, month, start_date, end_date)
        else:
            return self._generate_markdown_report(news_items, month, start_date, end_date)

    def _generate_markdown_report(
        self,
        news_items: List[NewsItem],
        month: str,
        start_date: str,
        end_date: str
    ) -> str:
        """Generate markdown format report"""
        # Analytics
        high_relevance = [n for n in news_items if n.korea_relevance_score >= 4]
        commitments = [n for n in news_items if n.category == '신규_출자_약정']

        by_lp = self._group_by_lp(news_items)
        by_category = self._group_by_category(news_items)
        by_sector = self._analyze_sectors(news_items)

        total_commitment = sum(n.amount for n in commitments if n.amount) or 0

        # Build report
        report = f"""# LP 투자 동향 월간 리포트
**기간**: {month} ({start_date} ~ {end_date})
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 월간 통계

### 전체 개요
- **총 뉴스 수**: {len(news_items)}개
- **한국 관련 고득점 시그널**: {len(high_relevance)}개 ({len(high_relevance)/max(len(news_items), 1)*100:.1f}%)
- **활동 LP 수**: {len(by_lp)}개
- **카테고리 수**: {len(by_category)}개

### 투자 활동
- **신규 커밋먼트**: {len(commitments)}건
- **총 커밋먼트 금액**: ${total_commitment:,.0f}
- **평균 커밋먼트 금액**: ${total_commitment/max(len(commitments), 1):,.0f}

"""

        # Monthly highlights
        report += "## 🌟 이번 달 하이라이트\n\n"
        highlights = self._generate_highlights(news_items, by_lp, commitments)
        for i, highlight in enumerate(highlights, 1):
            report += f"{i}. {highlight}\n"
        report += "\n"

        # LP activity ranking
        if by_lp:
            report += "## 🏆 LP별 활동 순위\n\n"
            lp_ranking = sorted(
                by_lp.items(),
                key=lambda x: (
                    sum(n.korea_relevance_score for n in x[1]),
                    len(x[1])
                ),
                reverse=True
            )

            report += "| 순위 | LP | 뉴스 수 | 고득점 | 평균 스코어 |\n"
            report += "|---|---|---|---|---|\n"

            for rank, (lp_name, news_list) in enumerate(lp_ranking[:15], 1):
                high_score = sum(1 for n in news_list if n.korea_relevance_score >= 4)
                avg_score = sum(n.korea_relevance_score for n in news_list) / len(news_list)

                report += f"| {rank} | {lp_name} | {len(news_list)} | {high_score} | {avg_score:.1f} |\n"

            report += "\n"

        # Category breakdown
        if by_category:
            report += "## 📂 카테고리 분석\n\n"
            category_sorted = sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)

            report += "| 카테고리 | 건수 | 비율 |\n"
            report += "|---|---|---|\n"

            for category, news_list in category_sorted:
                percentage = len(news_list) / len(news_items) * 100
                report += f"| {category} | {len(news_list)} | {percentage:.1f}% |\n"

            report += "\n"

        # Sector analysis
        if by_sector:
            report += "## 🎯 섹터별 투자 트렌드\n\n"
            sector_sorted = sorted(by_sector.items(), key=lambda x: x[1], reverse=True)

            report += "| 섹터 | 언급 횟수 |\n"
            report += "|---|---|\n"

            for sector, count in sector_sorted[:15]:
                report += f"| {sector} | {count} |\n"

            report += "\n"

            # Sector insights
            top_sectors = sector_sorted[:5]
            report += "**주요 섹터 인사이트:**\n"
            for sector, count in top_sectors:
                report += f"- **{sector}**: {count}건 언급 - "

                # Find LPs interested in this sector
                lps = set()
                for news in news_items:
                    if sector in news.sectors:
                        lps.add(news.lp_name)

                report += f"{', '.join(list(lps)[:3])}"
                if len(lps) > 3:
                    report += f" 외 {len(lps)-3}개 LP"
                report += "\n"

            report += "\n"

        # Regional focus
        report += "## 🌏 지역별 관심도\n\n"
        korea_count = len([n for n in news_items if n.korea_relevance_score >= 4])
        asia_count = len([n for n in news_items if any('asia' in tag.lower() for tag in n.tags)])

        report += f"- **한국 직접 관련**: {korea_count}건\n"
        report += f"- **아시아 지역**: {asia_count}건\n"
        report += f"- **기타**: {len(news_items) - korea_count - asia_count}건\n\n"

        # Top news items
        report += "## 🔥 주요 뉴스 (Top 10)\n\n"
        top_news = sorted(
            news_items,
            key=lambda x: (x.korea_relevance_score, x.amount or 0),
            reverse=True
        )[:10]

        for i, news in enumerate(top_news, 1):
            stars = "⭐" * news.korea_relevance_score
            report += f"### {i}. {news.lp_name} - {news.title} {stars}\n\n"

            if news.content_summary:
                report += f"{news.content_summary}\n\n"

            report += f"- **날짜**: {news.date}\n"
            report += f"- **카테고리**: {news.category}\n"

            if news.amount:
                report += f"- **금액**: ${news.amount:,.0f}\n"

            if news.sectors:
                report += f"- **섹터**: {', '.join(news.sectors)}\n"

            report += f"\n[원문 보기]({news.url})\n\n---\n\n"

        # Trends and insights
        report += "## 📈 트렌드 및 시사점\n\n"
        trends = self._analyze_trends(news_items, by_lp, by_sector)
        for trend in trends:
            report += f"### {trend['title']}\n\n"
            report += f"{trend['description']}\n\n"

        # Action items
        report += "## 💼 액션 아이템 및 권장사항\n\n"
        actions = self._generate_action_items(news_items, high_relevance, by_lp)
        for i, action in enumerate(actions, 1):
            report += f"{i}. {action}\n"

        report += "\n---\n\n"
        report += f"*본 리포트는 자동 생성되었습니다. ({datetime.now().strftime('%Y-%m-%d %H:%M')})*\n"

        return report

    def _group_by_lp(self, news_items: List[NewsItem]) -> Dict[str, List[NewsItem]]:
        """Group news by LP"""
        by_lp = {}
        for news in news_items:
            if news.lp_name not in by_lp:
                by_lp[news.lp_name] = []
            by_lp[news.lp_name].append(news)
        return by_lp

    def _group_by_category(self, news_items: List[NewsItem]) -> Dict[str, List[NewsItem]]:
        """Group news by category"""
        by_category = {}
        for news in news_items:
            if news.category:
                if news.category not in by_category:
                    by_category[news.category] = []
                by_category[news.category].append(news)
        return by_category

    def _analyze_sectors(self, news_items: List[NewsItem]) -> Dict[str, int]:
        """Analyze sector mentions"""
        all_sectors = []
        for news in news_items:
            all_sectors.extend(news.sectors)

        return dict(Counter(all_sectors))

    def _generate_highlights(
        self,
        news_items: List[NewsItem],
        by_lp: Dict,
        commitments: List[NewsItem]
    ) -> List[str]:
        """Generate monthly highlights"""
        highlights = []

        # Largest commitment
        if commitments:
            largest = max(commitments, key=lambda x: x.amount or 0)
            if largest.amount:
                highlights.append(
                    f"최대 규모 커밋먼트: {largest.lp_name}의 ${largest.amount:,.0f} 투자"
                )

        # Most active LP
        if by_lp:
            most_active = max(by_lp.items(), key=lambda x: len(x[1]))
            highlights.append(
                f"가장 활발한 LP: {most_active[0]} ({len(most_active[1])}건의 뉴스)"
            )

        # Korea interest
        high_korea = [n for n in news_items if n.korea_relevance_score >= 4]
        if high_korea:
            korea_lps = set(n.lp_name for n in high_korea)
            highlights.append(
                f"한국 관련 활동: {len(korea_lps)}개 LP에서 {len(high_korea)}건의 고득점 시그널"
            )

        return highlights

    def _analyze_trends(
        self,
        news_items: List[NewsItem],
        by_lp: Dict,
        by_sector: Dict
    ) -> List[Dict]:
        """Analyze trends"""
        trends = []

        # Sector trend
        if by_sector:
            top_sectors = sorted(by_sector.items(), key=lambda x: x[1], reverse=True)[:3]
            trend = {
                'title': '주요 섹터 트렌드',
                'description': f"이번 달 가장 주목받은 섹터는 {', '.join(s[0] for s in top_sectors)}입니다. "
                              f"특히 {top_sectors[0][0]} 섹터가 {top_sectors[0][1]}회 언급되며 가장 높은 관심을 받았습니다."
            }
            trends.append(trend)

        # LP activity trend
        active_lps = [lp for lp, news in by_lp.items() if len(news) >= 3]
        if active_lps:
            trend = {
                'title': 'LP 활동 증가',
                'description': f"{len(active_lps)}개 LP가 3건 이상의 뉴스를 발생시키며 활발한 활동을 보였습니다. "
                              f"주요 LP: {', '.join(active_lps[:5])}"
            }
            trends.append(trend)

        return trends

    def _generate_action_items(
        self,
        news_items: List[NewsItem],
        high_relevance: List[NewsItem],
        by_lp: Dict
    ) -> List[str]:
        """Generate action items"""
        actions = []

        if high_relevance:
            priority_lps = list(set(n.lp_name for n in high_relevance))
            actions.append(
                f"우선 접촉 LP: {', '.join(priority_lps[:5])} - 한국 관련 관심도 높음"
            )

        # Active LPs
        active_lps = sorted(by_lp.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        actions.append(
            f"활발한 LP 모니터링 강화: {', '.join(lp for lp, _ in active_lps)}"
        )

        actions.append("분기별 심층 분석 리포트 작성 고려")
        actions.append("LP 데이터베이스 정기 업데이트")

        return actions

    def save_report(
        self,
        report: str,
        filename: str = None,
        output_dir: str = "reports/monthly"
    ) -> str:
        """Save report to file"""
        if not filename:
            month = datetime.now().strftime('%Y%m')
            filename = f"monthly_report_{month}.md"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Report saved to: {filepath}")
        return str(filepath)
