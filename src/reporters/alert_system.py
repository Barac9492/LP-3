"""
Alert system for high-priority LP news
Sends email and Slack notifications for important signals
"""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import json

import requests

from ..database.models import NewsItem

logger = logging.getLogger(__name__)


class AlertSystem:
    """Sends alerts for high-priority LP news"""

    def __init__(self, config: Dict = None):
        """Initialize alert system"""
        self.config = config or {}

        # Email configuration
        self.email_enabled = self.config.get('alerts', {}).get('email', {}).get('enabled', False)
        self.smtp_server = self.config.get('alerts', {}).get('email', {}).get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('alerts', {}).get('email', {}).get('smtp_port', 587)
        self.from_address = os.getenv('EMAIL_ADDRESS', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.to_addresses = os.getenv('EMAIL_RECIPIENTS', '').split(',')

        # Slack configuration
        self.slack_enabled = self.config.get('alerts', {}).get('slack', {}).get('enabled', False)
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')

        # Alert thresholds
        thresholds = self.config.get('alerts', {}).get('thresholds', {})
        self.high_relevance_score = thresholds.get('high_relevance_score', 4)
        self.large_commitment_usd = thresholds.get('large_commitment_usd', 500_000_000)
        self.immediate_alert_score = thresholds.get('immediate_alert_score', 5)

    def should_alert(self, news: NewsItem) -> bool:
        """Check if news item should trigger an alert"""
        # High Korea relevance
        if news.korea_relevance_score >= self.immediate_alert_score:
            return True

        # Large commitment
        if news.amount and news.amount >= self.large_commitment_usd:
            return True

        # Korea-related category
        if news.category == '한국_관련':
            return True

        return False

    def send_alert(self, news: NewsItem, alert_type: str = "high_relevance"):
        """Send alert for a news item"""
        logger.info(f"Sending alert for: {news.title}")

        # Send email
        if self.email_enabled and self.from_address and self.to_addresses:
            try:
                self._send_email_alert(news, alert_type)
            except Exception as e:
                logger.error(f"Error sending email alert: {e}")

        # Send Slack
        if self.slack_enabled and self.slack_webhook:
            try:
                self._send_slack_alert(news, alert_type)
            except Exception as e:
                logger.error(f"Error sending Slack alert: {e}")

    def send_batch_alert(self, news_items: List[NewsItem], subject: str = "LP 뉴스 요약"):
        """Send batch alert for multiple news items"""
        if not news_items:
            return

        logger.info(f"Sending batch alert for {len(news_items)} items")

        # Send email
        if self.email_enabled and self.from_address and self.to_addresses:
            try:
                self._send_batch_email(news_items, subject)
            except Exception as e:
                logger.error(f"Error sending batch email: {e}")

        # Send Slack
        if self.slack_enabled and self.slack_webhook:
            try:
                self._send_batch_slack(news_items, subject)
            except Exception as e:
                logger.error(f"Error sending batch Slack message: {e}")

    def _send_email_alert(self, news: NewsItem, alert_type: str):
        """Send email alert for a single news item"""
        stars = "⭐" * news.korea_relevance_score

        subject = f"🔔 LP Alert: {news.lp_name} - {alert_type.upper()}"

        body = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; }}
.alert {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0; }}
.high-score {{ background: #d4edda; padding: 15px; border-left: 4px solid #28a745; }}
.details {{ background: #f8f9fa; padding: 10px; margin: 10px 0; }}
</style>
</head>
<body>
<h2>🔔 LP Investment Alert</h2>

<div class="alert">
<h3>{news.lp_name} - {news.title} {stars}</h3>
<p><strong>Date:</strong> {news.date}</p>
<p><strong>Category:</strong> {news.category}</p>
<p><strong>Korea Relevance Score:</strong> {news.korea_relevance_score}/5</p>
</div>

<div class="details">
{f"<p><strong>Summary:</strong><br>{news.content_summary}</p>" if news.content_summary else ""}

{f"<p><strong>Amount:</strong> ${news.amount:,.0f}</p>" if news.amount else ""}

{f"<p><strong>Sectors:</strong> {', '.join(news.sectors)}</p>" if news.sectors else ""}

{f"<p><strong>Key Points:</strong></p><ul>{''.join(f'<li>{point}</li>' for point in news.key_points)}</ul>" if news.key_points else ""}

{f"<p><strong>Action Items:</strong></p><ul>{''.join(f'<li>{item}</li>' for item in news.action_items)}</ul>" if news.action_items else ""}

<p><a href="{news.url}">Read Full Article</a></p>
</div>

<p><em>This is an automated alert from LP Monitoring System</em></p>
</body>
</html>
"""

        self._send_email(subject, body, html=True)

    def _send_batch_email(self, news_items: List[NewsItem], subject: str):
        """Send batch email for multiple news items"""
        news_html = ""

        for news in news_items[:10]:  # Limit to 10
            stars = "⭐" * news.korea_relevance_score
            news_html += f"""
<div class="news-item">
<h3>{news.lp_name} - {news.title} {stars}</h3>
<p><strong>Date:</strong> {news.date} | <strong>Score:</strong> {news.korea_relevance_score}/5</p>
{f"<p>{news.content_summary}</p>" if news.content_summary else ""}
<p><a href="{news.url}">Read More</a></p>
</div>
<hr>
"""

        body = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; }}
.news-item {{ margin: 20px 0; }}
</style>
</head>
<body>
<h2>{subject}</h2>
<p>Found {len(news_items)} high-relevance news items:</p>

{news_html}

<p><em>This is an automated report from LP Monitoring System</em></p>
</body>
</html>
"""

        self._send_email(subject, body, html=True)

    def _send_email(self, subject: str, body: str, html: bool = False):
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_address
        msg['To'] = ', '.join(self.to_addresses)

        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.from_address, self.email_password)
            server.send_message(msg)

        logger.info(f"Email sent to {len(self.to_addresses)} recipients")

    def _send_slack_alert(self, news: NewsItem, alert_type: str):
        """Send Slack alert for a single news item"""
        stars = "⭐" * news.korea_relevance_score

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 LP Alert: {alert_type.upper()}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{news.lp_name}* - {news.title} {stars}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:*\n{news.date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Category:*\n{news.category}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Score:*\n{news.korea_relevance_score}/5"
                    }
                ]
            }
        ]

        if news.content_summary:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{news.content_summary}"
                }
            })

        if news.amount:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Amount:* ${news.amount:,.0f}"
                }
            })

        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Read Full Article"
                    },
                    "url": news.url
                }
            ]
        })

        payload = {
            "blocks": blocks
        }

        response = requests.post(self.slack_webhook, json=payload)
        response.raise_for_status()

        logger.info("Slack alert sent successfully")

    def _send_batch_slack(self, news_items: List[NewsItem], subject: str):
        """Send batch Slack message"""
        text = f"*{subject}*\n\nFound {len(news_items)} high-relevance items:\n\n"

        for i, news in enumerate(news_items[:10], 1):
            stars = "⭐" * news.korea_relevance_score
            text += f"{i}. *{news.lp_name}* - {news.title} {stars}\n"
            text += f"   Score: {news.korea_relevance_score}/5 | <{news.url}|Read More>\n\n"

        payload = {
            "text": text
        }

        response = requests.post(self.slack_webhook, json=payload)
        response.raise_for_status()

        logger.info("Batch Slack message sent successfully")

    def test_alert(self):
        """Send test alert to verify configuration"""
        logger.info("Sending test alert...")

        # Create test news
        test_news = NewsItem(
            lp_name="Test LP",
            title="Test Alert - LP Monitoring System",
            url="https://example.com",
            date="2024-12-10",
            content_summary="This is a test alert to verify the alert system configuration.",
            category="일반_소식",
            korea_relevance_score=5
        )

        self.send_alert(test_news, alert_type="test")
        logger.info("Test alert sent successfully")
