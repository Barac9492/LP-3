"""
Korea relevance scorer
Assigns relevance scores to news items based on Korea interest
"""
import logging
import re
from typing import List, Dict

from ..database.models import NewsItem

logger = logging.getLogger(__name__)


class KoreaRelevanceScorer:
    """Scores news items for Korea VC relevance"""

    def __init__(self, config: Dict = None):
        """Initialize scorer with configuration"""
        self.config = config or {}

        # Scoring weights from config
        self.weights = self.config.get('scoring', {}).get('keywords', {
            'korea_direct': 5,
            'korea_company': 5,
            'asia_focus': 4,
            'emerging_markets': 3,
            'relevant_sector': 3,
            'venture_general': 2
        })

        # Sectors of interest
        self.sectors_of_interest = self.config.get('scoring', {}).get(
            'sectors_of_interest',
            ['AI', 'semiconductor', 'biotech', 'fintech', 'consumer', 'enterprise software']
        )

        # Minimum commitment threshold
        self.min_commitment = self.config.get('scoring', {}).get(
            'minimum_commitment_usd',
            100_000_000
        )

        # Keywords
        self.korea_keywords = [
            'korea', 'korean', 'seoul', 'kospi', 'kosdaq',
            'samsung', 'lg', 'hyundai', 'sk', 'naver', 'kakao'
        ]

        self.asia_keywords = [
            'asia', 'asian', 'asia-pacific', 'apac', 'east asia',
            'southeast asia', 'emerging asia'
        ]

        self.emerging_keywords = [
            'emerging market', 'emerging economy', 'developing market'
        ]

        self.venture_keywords = [
            'venture capital', 'startup', 'vc', 'early stage',
            'growth equity', 'late stage'
        ]

    def score(self, news: NewsItem) -> NewsItem:
        """Calculate Korea relevance score for a news item"""
        score = 0
        text = (news.title + ' ' + (news.content or '')).lower()

        # Check for direct Korea mentions (Score: 5)
        if self._contains_keywords(text, self.korea_keywords):
            score = max(score, 5)
            news.tags.append('korea_direct')
            logger.debug(f"Korea direct mention: +5 points")

        # Check for Korea category (Score: 5)
        elif news.category == '한국_관련':
            score = max(score, 5)
            news.tags.append('korea_category')

        # Check for Asia focus (Score: 4)
        elif self._contains_keywords(text, self.asia_keywords):
            score = max(score, 4)
            news.tags.append('asia_focus')
            logger.debug(f"Asia focus: +4 points")

        # Check for emerging markets (Score: 3)
        elif self._contains_keywords(text, self.emerging_keywords):
            score = max(score, 3)
            news.tags.append('emerging_markets')
            logger.debug(f"Emerging markets: +3 points")

        # Check for relevant sectors (Score: 3 if Asia/Korea, else 2)
        sector_match = self._check_sectors(text)
        if sector_match:
            news.sectors.extend(sector_match)
            if score >= 3:  # If already Asia/Korea related
                score = max(score, 4)
                logger.debug(f"Relevant sectors + Asia/Korea: +4 points")
            else:
                score = max(score, 2)
                logger.debug(f"Relevant sectors: +2 points")

        # Check for venture/PE general (Score: 2)
        elif self._contains_keywords(text, self.venture_keywords):
            score = max(score, 2)
            news.tags.append('venture_general')
            logger.debug(f"Venture/PE general: +2 points")

        # Boost score for new commitments (Score: +1)
        if news.category == '신규_출자_약정':
            if news.amount and news.amount >= self.min_commitment:
                score = min(score + 1, 5)
                news.tags.append('large_commitment')
                logger.debug(f"Large commitment: +1 point boost")

        # Ensure score is in valid range
        score = max(1, min(5, score))

        news.korea_relevance_score = score
        logger.debug(f"Final Korea relevance score: {score}")

        return news

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords"""
        return any(keyword in text for keyword in keywords)

    def _check_sectors(self, text: str) -> List[str]:
        """Check if text mentions any sectors of interest"""
        matched_sectors = []

        for sector in self.sectors_of_interest:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(sector.lower()) + r'\b'
            if re.search(pattern, text):
                matched_sectors.append(sector)

        return matched_sectors

    def score_batch(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Score multiple news items"""
        scored = []

        for news in news_items:
            scored_news = self.score(news)
            scored.append(scored_news)

        logger.info(f"Scored {len(scored)} news items")

        # Log distribution
        distribution = {}
        for news in scored:
            score = news.korea_relevance_score
            distribution[score] = distribution.get(score, 0) + 1

        logger.info(f"Score distribution: {distribution}")

        return scored

    def get_high_relevance_items(
        self,
        news_items: List[NewsItem],
        threshold: int = 4
    ) -> List[NewsItem]:
        """Get news items with high relevance scores"""
        return [
            news for news in news_items
            if news.korea_relevance_score >= threshold
        ]
