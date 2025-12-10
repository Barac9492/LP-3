"""
News summarizer using AI
Creates concise summaries of news articles
"""
import logging
import os
from typing import Optional

from ..database.models import NewsItem

logger = logging.getLogger(__name__)


class NewsSummarizer:
    """Creates summaries of news articles using AI"""

    def __init__(
        self,
        api_provider: str = "openai",
        model: str = "gpt-4",
        temperature: float = 0.3
    ):
        """Initialize summarizer"""
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
                    logger.info("OpenAI client initialized for summarization")
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
                    logger.info("Anthropic client initialized for summarization")
                else:
                    logger.warning("ANTHROPIC_API_KEY not set")
            except ImportError:
                logger.error("anthropic package not installed")

    def summarize(self, news: NewsItem, language: str = "ko") -> str:
        """Create a summary of the news article"""
        if not self.client:
            logger.warning("AI client not initialized, using fallback summary")
            return self._fallback_summary(news)

        try:
            content = news.content or news.title

            if language == "ko":
                lang_instruction = "한국어로 요약해주세요."
            else:
                lang_instruction = "Summarize in English."

            prompt = f"""Summarize this news article in 2-3 sentences. {lang_instruction}

Title: {news.title}
Content: {content[:3000]}

Focus on:
1. What happened (commitment amount, investment, strategy change, etc.)
2. Why it matters for Korea VC fundraising
3. Any actionable insights

Summary:"""

            if self.api_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a concise financial news summarizer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=300
                )
                summary = response.choices[0].message.content.strip()

            elif self.api_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                summary = response.content[0].text.strip()

            else:
                summary = self._fallback_summary(news)

            return summary

        except Exception as e:
            logger.error(f"Error creating summary: {e}")
            return self._fallback_summary(news)

    def _fallback_summary(self, news: NewsItem) -> str:
        """Create a simple summary without AI"""
        # Just use the title and first part of content
        if news.content and len(news.content) > 100:
            return f"{news.title}. {news.content[:200]}..."
        return news.title

    def create_executive_summary(
        self,
        news_items: list[NewsItem],
        language: str = "ko"
    ) -> str:
        """Create an executive summary of multiple news items"""
        if not news_items:
            return "No news items to summarize."

        if not self.client:
            return self._fallback_executive_summary(news_items)

        try:
            # Prepare news summaries
            news_text = "\n\n".join([
                f"{i+1}. {news.lp_name} - {news.title} (Score: {news.korea_relevance_score})"
                for i, news in enumerate(news_items[:10])  # Limit to top 10
            ])

            if language == "ko":
                lang_instruction = "한국어로 작성해주세요."
            else:
                lang_instruction = "Write in English."

            prompt = f"""Create an executive summary of these LP news items. {lang_instruction}

{news_text}

Provide:
1. 3-5 key takeaways (핵심 요약)
2. Trends and patterns
3. Action items for Korea VC fundraising

Executive Summary:"""

            if self.api_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a financial analyst creating executive summaries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=800
                )
                summary = response.choices[0].message.content.strip()

            elif self.api_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                summary = response.content[0].text.strip()

            else:
                summary = self._fallback_executive_summary(news_items)

            return summary

        except Exception as e:
            logger.error(f"Error creating executive summary: {e}")
            return self._fallback_executive_summary(news_items)

    def _fallback_executive_summary(self, news_items: list[NewsItem]) -> str:
        """Create a simple executive summary without AI"""
        high_score = [n for n in news_items if n.korea_relevance_score >= 4]

        summary = f"Collected {len(news_items)} news items.\n"
        summary += f"High relevance items: {len(high_score)}\n\n"

        if high_score:
            summary += "Top items:\n"
            for i, news in enumerate(high_score[:5], 1):
                summary += f"{i}. {news.lp_name}: {news.title}\n"

        return summary
