"""
News collector for LP institutions
Searches and collects news articles about LP investment activities
"""
import logging
import time
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from ..database.models import NewsItem
from .lp_profiles import LPProfileManager
from .search_queries import SearchQueryGenerator

logger = logging.getLogger(__name__)


class NewsCollector:
    """Collects news articles about LP institutions"""

    def __init__(
        self,
        lp_manager: LPProfileManager,
        query_generator: SearchQueryGenerator,
        request_delay: float = 1.0,
        timeout: int = 30
    ):
        """Initialize news collector"""
        self.lp_manager = lp_manager
        self.query_generator = query_generator
        self.request_delay = request_delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def collect_news_for_lp(
        self,
        lp_name: str,
        days: int = 7,
        max_results: int = 10
    ) -> List[NewsItem]:
        """Collect news for a specific LP institution"""
        logger.info(f"Collecting news for {lp_name}...")

        try:
            profile = self.lp_manager.get_profile(lp_name)
            queries = self.query_generator.generate_queries_for_lp(
                lp_name,
                profile.search_keywords,
                max_queries=3
            )

            all_news = []
            seen_urls = set()

            for query in queries:
                logger.debug(f"Searching: {query}")
                results = self._search_web(query, max_results=5)

                for result in results:
                    # Skip duplicates
                    if result['url'] in seen_urls:
                        continue

                    # Create news item
                    news = NewsItem(
                        lp_name=lp_name,
                        title=result['title'],
                        url=result['url'],
                        date=result.get('date', datetime.now().strftime('%Y-%m-%d')),
                        content=result.get('snippet', ''),
                        source=result.get('source', 'web_search')
                    )

                    all_news.append(news)
                    seen_urls.add(result['url'])

                    if len(all_news) >= max_results:
                        break

                if len(all_news) >= max_results:
                    break

                # Rate limiting
                time.sleep(self.request_delay)

            logger.info(f"Collected {len(all_news)} news items for {lp_name}")
            return all_news[:max_results]

        except Exception as e:
            logger.error(f"Error collecting news for {lp_name}: {e}")
            return []

    def collect_news_for_all_lps(
        self,
        lp_names: List[str],
        days: int = 7,
        max_results_per_lp: int = 10
    ) -> Dict[str, List[NewsItem]]:
        """Collect news for multiple LP institutions"""
        logger.info(f"Collecting news for {len(lp_names)} LPs...")

        results = {}

        for lp_name in lp_names:
            news_items = self.collect_news_for_lp(
                lp_name,
                days=days,
                max_results=max_results_per_lp
            )
            results[lp_name] = news_items

            # Rate limiting between LPs
            time.sleep(self.request_delay)

        total_news = sum(len(items) for items in results.values())
        logger.info(f"Collected total of {total_news} news items")

        return results

    def _search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search the web for news articles
        This is a basic implementation that can be enhanced with proper search APIs
        """
        results = []

        try:
            # Use DuckDuckGo HTML search (no API key required)
            # Note: For production, consider using proper APIs like SerpAPI, NewsAPI, etc.
            search_url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query + ' news',
            }

            response = self.session.post(
                search_url,
                data=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                search_results = soup.find_all('div', class_='result')

                for result in search_results[:max_results]:
                    try:
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')

                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')

                            # Extract actual URL from DuckDuckGo redirect
                            if 'uddg=' in url:
                                import urllib.parse
                                url = urllib.parse.unquote(url.split('uddg=')[1])

                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

                            # Try to extract date from snippet
                            date = self._extract_date_from_text(snippet)

                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'date': date,
                                'source': 'duckduckgo'
                            })

                    except Exception as e:
                        logger.debug(f"Error parsing search result: {e}")
                        continue

            logger.debug(f"Found {len(results)} search results for: {query}")

        except Exception as e:
            logger.error(f"Error searching web: {e}")

        return results

    def _extract_date_from_text(self, text: str) -> str:
        """Extract date from text, return today's date if not found"""
        # Look for common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group()
                try:
                    # Try to parse and normalize to YYYY-MM-DD
                    if '-' in date_str and len(date_str) == 10:
                        return date_str
                    # Add more date parsing as needed
                except:
                    pass

        # Default to today
        return datetime.now().strftime('%Y-%m-%d')

    def fetch_article_content(self, url: str) -> Optional[str]:
        """Fetch full article content from URL"""
        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove script and style elements
                for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                    script.decompose()

                # Get text content
                text = soup.get_text(separator=' ', strip=True)

                # Clean up whitespace
                text = ' '.join(text.split())

                return text[:10000]  # Limit to 10k characters

        except Exception as e:
            logger.debug(f"Error fetching article content: {e}")

        return None

    def enhance_news_with_content(self, news: NewsItem) -> NewsItem:
        """Fetch and add full article content to news item"""
        if not news.content or len(news.content) < 100:
            content = self.fetch_article_content(news.url)
            if content:
                news.content = content

        return news
