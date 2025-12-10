"""
Tests for database models
"""
import pytest
from datetime import datetime

from src.database.models import NewsItem, LPProfile, CollectionRun


class TestNewsItem:
    """Test NewsItem model"""

    def test_create_news_item(self):
        """Test creating a news item"""
        news = NewsItem(
            lp_name="GIC",
            title="Test News",
            url="https://example.com/news",
            date="2024-12-10"
        )

        assert news.lp_name == "GIC"
        assert news.title == "Test News"
        assert news.url == "https://example.com/news"
        assert news.date == "2024-12-10"
        assert news.id is not None  # Auto-generated
        assert news.collected_at is not None  # Auto-generated

    def test_news_item_to_dict(self):
        """Test converting news item to dictionary"""
        news = NewsItem(
            lp_name="GIC",
            title="Test",
            url="https://example.com",
            date="2024-12-10",
            korea_relevance_score=4
        )

        data = news.to_dict()

        assert isinstance(data, dict)
        assert data['lp_name'] == "GIC"
        assert data['korea_relevance_score'] == 4

    def test_is_high_relevance(self):
        """Test high relevance check"""
        news1 = NewsItem(
            lp_name="GIC",
            title="Test",
            url="https://example.com",
            date="2024-12-10",
            korea_relevance_score=5
        )

        news2 = NewsItem(
            lp_name="GIC",
            title="Test",
            url="https://example.com/2",
            date="2024-12-10",
            korea_relevance_score=2
        )

        assert news1.is_high_relevance() is True
        assert news2.is_high_relevance() is False

    def test_is_large_commitment(self):
        """Test large commitment check"""
        news1 = NewsItem(
            lp_name="GIC",
            title="Test",
            url="https://example.com",
            date="2024-12-10",
            amount=500_000_000
        )

        news2 = NewsItem(
            lp_name="GIC",
            title="Test",
            url="https://example.com/2",
            date="2024-12-10",
            amount=50_000_000
        )

        assert news1.is_large_commitment() is True
        assert news2.is_large_commitment() is False


class TestLPProfile:
    """Test LPProfile model"""

    def test_create_lp_profile(self):
        """Test creating LP profile"""
        profile = LPProfile(
            name="GIC",
            full_name="GIC Private Limited",
            country="Singapore",
            aum=690_000_000_000,
            pe_allocation_pct=12,
            focus_regions=["Asia", "Global"],
            website="https://www.gic.com.sg",
            korea_interest="high",
            search_keywords=["GIC investment"]
        )

        assert profile.name == "GIC"
        assert profile.country == "Singapore"
        assert profile.korea_interest == "high"

    def test_lp_profile_to_dict(self):
        """Test converting LP profile to dictionary"""
        profile = LPProfile(
            name="GIC",
            full_name="GIC Private Limited",
            country="Singapore",
            aum=690_000_000_000,
            pe_allocation_pct=12,
            focus_regions=["Asia"],
            website="https://www.gic.com.sg",
            korea_interest="high",
            search_keywords=["GIC"]
        )

        data = profile.to_dict()

        assert isinstance(data, dict)
        assert data['name'] == "GIC"
        assert data['aum'] == 690_000_000_000


class TestCollectionRun:
    """Test CollectionRun model"""

    def test_create_collection_run(self):
        """Test creating collection run"""
        run = CollectionRun(
            id="20241210_120000",
            start_time="2024-12-10T12:00:00"
        )

        assert run.id == "20241210_120000"
        assert run.status == "running"
        assert run.news_collected == 0

    def test_collection_run_to_dict(self):
        """Test converting collection run to dictionary"""
        run = CollectionRun(
            id="20241210_120000",
            start_time="2024-12-10T12:00:00",
            status="completed",
            news_collected=10
        )

        data = run.to_dict()

        assert isinstance(data, dict)
        assert data['status'] == "completed"
        assert data['news_collected'] == 10
