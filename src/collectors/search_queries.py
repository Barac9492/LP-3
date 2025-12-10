"""
Search query generation for LP news collection
"""
import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SearchQueryGenerator:
    """Generates search queries for LP news collection"""

    def __init__(self, keywords_path: str = "data/search_keywords.json"):
        """Initialize search query generator"""
        self.keywords_path = Path(keywords_path)
        self.keywords: Dict[str, List[str]] = {}
        self.load_keywords()

    def load_keywords(self):
        """Load search keywords from JSON file"""
        try:
            with open(self.keywords_path, 'r', encoding='utf-8') as f:
                self.keywords = json.load(f)

            logger.info(f"Loaded {len(self.keywords)} keyword categories")

        except FileNotFoundError:
            logger.error(f"Keywords file not found: {self.keywords_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing keywords JSON: {e}")
            raise

    def generate_queries_for_lp(
        self,
        lp_name: str,
        lp_keywords: List[str],
        max_queries: int = 5
    ) -> List[str]:
        """Generate search queries for a specific LP"""
        queries = []

        # Use LP-specific keywords
        for keyword in lp_keywords[:max_queries]:
            queries.append(keyword)

        # Combine with investment activity keywords
        if len(queries) < max_queries:
            for activity in self.keywords.get('investment_activities', [])[:2]:
                query = f"{lp_name} {activity}"
                queries.append(query)
                if len(queries) >= max_queries:
                    break

        return queries[:max_queries]

    def generate_korea_focused_query(self, lp_name: str) -> str:
        """Generate a Korea-focused search query"""
        return f"{lp_name} Korea investment OR Korean startups OR Asia venture capital"

    def generate_sector_query(self, lp_name: str, sector: str) -> str:
        """Generate a sector-specific search query"""
        return f"{lp_name} {sector} investment"

    def generate_recent_news_query(
        self,
        lp_name: str,
        days: int = 7
    ) -> str:
        """Generate a query for recent news"""
        # Note: Date filtering is typically handled by the search API
        # This just creates the base query
        return f"{lp_name} investment news OR announcement OR commitment"

    def get_date_filter(self, days: int = 7) -> str:
        """Get date filter string for search"""
        start_date = datetime.now() - timedelta(days=days)
        return start_date.strftime('%Y-%m-%d')

    def get_all_korea_keywords(self) -> List[str]:
        """Get all Korea-related keywords"""
        return self.keywords.get('korea_related', [])

    def get_all_sector_keywords(self) -> List[str]:
        """Get all sector keywords"""
        return self.keywords.get('sectors', [])

    def is_korea_related(self, text: str) -> bool:
        """Check if text contains Korea-related keywords"""
        text_lower = text.lower()
        korea_keywords = self.get_all_korea_keywords()
        return any(keyword.lower() in text_lower for keyword in korea_keywords)

    def is_asia_related(self, text: str) -> bool:
        """Check if text contains Asia-related keywords"""
        text_lower = text.lower()
        asia_keywords = self.keywords.get('asia_related', [])
        return any(keyword.lower() in text_lower for keyword in asia_keywords)

    def extract_sectors(self, text: str) -> List[str]:
        """Extract sector keywords from text"""
        text_lower = text.lower()
        sectors = []

        for sector in self.get_all_sector_keywords():
            if sector.lower() in text_lower:
                sectors.append(sector)

        return sectors
