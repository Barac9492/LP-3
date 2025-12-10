"""
Tests for Korea relevance scorer
"""
import pytest

from src.analyzers.scorer import KoreaRelevanceScorer
from src.database.models import NewsItem


class TestKoreaRelevanceScorer:
    """Test Korea relevance scorer"""

    @pytest.fixture
    def scorer(self):
        """Create scorer instance"""
        return KoreaRelevanceScorer()

    def test_score_korea_direct(self, scorer):
        """Test scoring for direct Korea mentions"""
        news = NewsItem(
            lp_name="GIC",
            title="GIC invests in Korean AI startups",
            url="https://example.com",
            date="2024-12-10",
            content="GIC made significant investment in Seoul-based AI companies"
        )

        scored_news = scorer.score(news)

        assert scored_news.korea_relevance_score == 5
        assert 'korea_direct' in scored_news.tags

    def test_score_asia_focus(self, scorer):
        """Test scoring for Asia focus"""
        news = NewsItem(
            lp_name="GIC",
            title="GIC expands Asia-Pacific investments",
            url="https://example.com",
            date="2024-12-10",
            content="GIC announces major expansion in Asian markets"
        )

        scored_news = scorer.score(news)

        assert scored_news.korea_relevance_score >= 4
        assert 'asia_focus' in scored_news.tags

    def test_score_sector_relevance(self, scorer):
        """Test scoring for relevant sectors"""
        news = NewsItem(
            lp_name="GIC",
            title="GIC invests in semiconductor technology",
            url="https://example.com",
            date="2024-12-10",
            content="Major commitment to semiconductor and AI sectors"
        )

        scored_news = scorer.score(news)

        assert scored_news.korea_relevance_score >= 2
        assert 'semiconductor' in scored_news.sectors or 'AI' in scored_news.sectors

    def test_score_low_relevance(self, scorer):
        """Test scoring for low relevance news"""
        news = NewsItem(
            lp_name="CalPERS",
            title="CalPERS quarterly meeting",
            url="https://example.com",
            date="2024-12-10",
            content="Routine quarterly board meeting held"
        )

        scored_news = scorer.score(news)

        assert scored_news.korea_relevance_score <= 2

    def test_score_batch(self, scorer):
        """Test batch scoring"""
        news_items = [
            NewsItem(
                lp_name="GIC",
                title=f"News {i}",
                url=f"https://example.com/{i}",
                date="2024-12-10"
            )
            for i in range(5)
        ]

        scored_items = scorer.score_batch(news_items)

        assert len(scored_items) == 5
        for item in scored_items:
            assert 1 <= item.korea_relevance_score <= 5

    def test_get_high_relevance_items(self, scorer):
        """Test filtering high relevance items"""
        news_items = [
            NewsItem(
                lp_name="GIC",
                title="Korea investment",
                url="https://example.com/1",
                date="2024-12-10",
                korea_relevance_score=5
            ),
            NewsItem(
                lp_name="GIC",
                title="General news",
                url="https://example.com/2",
                date="2024-12-10",
                korea_relevance_score=2
            ),
            NewsItem(
                lp_name="GIC",
                title="Asia focus",
                url="https://example.com/3",
                date="2024-12-10",
                korea_relevance_score=4
            )
        ]

        high_relevance = scorer.get_high_relevance_items(news_items, threshold=4)

        assert len(high_relevance) == 2
        assert all(n.korea_relevance_score >= 4 for n in high_relevance)
