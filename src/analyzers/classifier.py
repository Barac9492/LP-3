"""
News classifier using AI
Classifies news articles into categories
"""
import json
import logging
import os
from typing import Optional, Dict

from ..database.models import NewsItem

logger = logging.getLogger(__name__)


class NewsClassifier:
    """Classifies news articles using AI"""

    CATEGORIES = [
        "신규_출자_약정",  # New commitment
        "전략_변화",      # Strategy change
        "인사_변동",      # Personnel change
        "성과_발표",      # Performance announcement
        "한국_관련",      # Korea-related
        "일반_소식",      # General news
    ]

    def __init__(
        self,
        api_provider: str = "openai",  # or "anthropic"
        model: str = "gpt-4",
        temperature: float = 0.3
    ):
        """Initialize classifier"""
        self.api_provider = api_provider.lower()
        self.model = model
        self.temperature = temperature
        self.client = None

        self._initialize_client()

    def _initialize_client(self):
        """Initialize AI API client"""
        if self.api_provider == "openai":
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized")
                else:
                    logger.warning("OPENAI_API_KEY not set")
            except ImportError:
                logger.error("openai package not installed")

        elif self.api_provider == "anthropic":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Anthropic client initialized")
                else:
                    logger.warning("ANTHROPIC_API_KEY not set")
            except ImportError:
                logger.error("anthropic package not installed")

    def classify(self, news: NewsItem) -> NewsItem:
        """Classify a news article"""
        if not self.client:
            logger.warning("AI client not initialized, using fallback classification")
            return self._fallback_classify(news)

        try:
            analysis = self._analyze_with_ai(news)

            if analysis:
                news.category = analysis.get('category', '일반_소식')
                news.content_summary = analysis.get('summary', '')
                news.key_points = analysis.get('key_points', [])
                news.action_items = analysis.get('action_items', [])

                # Extract financial info
                if 'amount' in analysis and analysis['amount']:
                    news.amount = analysis['amount']

                # Extract sectors
                if 'sectors' in analysis:
                    news.sectors = analysis['sectors']

            logger.debug(f"Classified news as: {news.category}")

        except Exception as e:
            logger.error(f"Error classifying news: {e}")
            news = self._fallback_classify(news)

        return news

    def _analyze_with_ai(self, news: NewsItem) -> Optional[Dict]:
        """Analyze news with AI API"""
        content = news.content or news.title

        prompt = f"""Analyze the following news article about {news.lp_name}:

Title: {news.title}
Content: {content[:2000]}

Classify this news and provide analysis in the following JSON format:
{{
  "category": "one of: 신규_출자_약정, 전략_변화, 인사_변동, 성과_발표, 한국_관련, 일반_소식",
  "summary": "2-3 sentence summary in Korean",
  "key_points": ["key point 1", "key point 2"],
  "action_items": ["actionable item 1", "actionable item 2"],
  "amount": <USD amount if mentioned, else null>,
  "sectors": ["sector1", "sector2"]
}}

Categories:
- 신규_출자_약정: New fund commitments or capital allocations
- 전략_변화: Changes in investment strategy or policy
- 인사_변동: CIO or key personnel changes
- 성과_발표: Performance reports or returns
- 한국_관련: Direct Korea or Korean company mentions
- 일반_소식: General news

Return only valid JSON."""

        try:
            if self.api_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a financial news analyst specializing in LP investments."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=1000
                )
                result = response.choices[0].message.content

            elif self.api_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.content[0].text

            else:
                return None

            # Parse JSON response
            # Clean up the response - remove markdown code blocks if present
            result = result.strip()
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
            result = result.strip()

            return json.loads(result)

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling AI API: {e}")
            return None

    def _fallback_classify(self, news: NewsItem) -> NewsItem:
        """Simple rule-based classification as fallback"""
        text = (news.title + ' ' + (news.content or '')).lower()

        # Keyword-based classification
        if any(word in text for word in ['commitment', 'committed', 'invest', 'allocation', 'capital']):
            news.category = '신규_출자_약정'
        elif any(word in text for word in ['korea', 'korean', 'seoul']):
            news.category = '한국_관련'
        elif any(word in text for word in ['cio', 'hire', 'appoint', 'resign', 'personnel']):
            news.category = '인사_변동'
        elif any(word in text for word in ['strategy', 'policy', 'shift', 'focus']):
            news.category = '전략_변화'
        elif any(word in text for word in ['return', 'performance', 'irr', 'profit']):
            news.category = '성과_발표'
        else:
            news.category = '일반_소식'

        # Simple summary
        news.content_summary = news.title

        logger.debug(f"Fallback classification: {news.category}")
        return news

    def classify_batch(self, news_items: list[NewsItem]) -> list[NewsItem]:
        """Classify multiple news items"""
        classified = []

        for news in news_items:
            classified_news = self.classify(news)
            classified.append(classified_news)

        return classified
