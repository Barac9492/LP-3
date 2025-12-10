"""
Database manager for LP monitoring system
Handles SQLite database operations
"""
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pathlib import Path

from .models import NewsItem, CollectionRun

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages the SQLite database for news storage"""

    def __init__(self, db_path: str = "data/news_archive.db"):
        """Initialize database manager"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self.initialize_db()

    def initialize_db(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # News items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_items (
                id TEXT PRIMARY KEY,
                lp_name TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                date TEXT NOT NULL,
                collected_at TEXT NOT NULL,
                content TEXT,
                content_summary TEXT,
                category TEXT,
                korea_relevance_score INTEGER DEFAULT 0,
                key_points TEXT,
                action_items TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                sectors TEXT,
                regions TEXT,
                tags TEXT,
                source TEXT,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Collection runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_runs (
                id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'running',
                lps_processed TEXT,
                news_collected INTEGER DEFAULT 0,
                errors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_lp_name ON news_items(lp_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_date ON news_items(date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_score ON news_items(korea_relevance_score)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON news_items(category)"
        )

        conn.commit()
        logger.info("Database initialized successfully")

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def save_news_item(self, news: NewsItem) -> bool:
        """Save a news item to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO news_items (
                    id, lp_name, title, url, date, collected_at,
                    content, content_summary, category, korea_relevance_score,
                    key_points, action_items, amount, currency,
                    sectors, regions, tags, source, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news.id,
                news.lp_name,
                news.title,
                news.url,
                news.date,
                news.collected_at,
                news.content,
                news.content_summary,
                news.category,
                news.korea_relevance_score,
                json.dumps(news.key_points),
                json.dumps(news.action_items),
                news.amount,
                news.currency,
                json.dumps(news.sectors),
                json.dumps(news.regions),
                json.dumps(news.tags),
                news.source,
                news.language
            ))

            conn.commit()
            logger.debug(f"Saved news item: {news.id}")
            return True

        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate news item: {news.url} - {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving news item: {e}")
            return False

    def get_news_by_id(self, news_id: str) -> Optional[NewsItem]:
        """Get a news item by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM news_items WHERE id = ?", (news_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_news_item(row)
        return None

    def get_news_by_lp(
        self,
        lp_name: str,
        days: int = 7,
        min_score: int = 0
    ) -> List[NewsItem]:
        """Get news items for a specific LP"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT * FROM news_items
            WHERE lp_name = ?
            AND date >= ?
            AND korea_relevance_score >= ?
            ORDER BY date DESC
        """, (lp_name, cutoff_date, min_score))

        return [self._row_to_news_item(row) for row in cursor.fetchall()]

    def get_recent_news(
        self,
        days: int = 7,
        min_score: int = 0,
        category: Optional[str] = None
    ) -> List[NewsItem]:
        """Get recent news items"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = """
            SELECT * FROM news_items
            WHERE date >= ?
            AND korea_relevance_score >= ?
        """
        params = [cutoff_date, min_score]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY date DESC, korea_relevance_score DESC"

        cursor.execute(query, params)
        return [self._row_to_news_item(row) for row in cursor.fetchall()]

    def get_high_relevance_news(self, days: int = 7, threshold: int = 4) -> List[NewsItem]:
        """Get high relevance news items"""
        return self.get_recent_news(days=days, min_score=threshold)

    def get_news_by_date_range(
        self,
        start_date: str,
        end_date: str,
        lp_name: Optional[str] = None
    ) -> List[NewsItem]:
        """Get news items within a date range"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if lp_name:
            cursor.execute("""
                SELECT * FROM news_items
                WHERE date BETWEEN ? AND ?
                AND lp_name = ?
                ORDER BY date DESC
            """, (start_date, end_date, lp_name))
        else:
            cursor.execute("""
                SELECT * FROM news_items
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (start_date, end_date))

        return [self._row_to_news_item(row) for row in cursor.fetchall()]

    def get_statistics(self, days: int = 7) -> Dict:
        """Get statistics about collected news"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Total news count
        cursor.execute(
            "SELECT COUNT(*) FROM news_items WHERE date >= ?",
            (cutoff_date,)
        )
        total_news = cursor.fetchone()[0]

        # High relevance count
        cursor.execute(
            "SELECT COUNT(*) FROM news_items WHERE date >= ? AND korea_relevance_score >= 4",
            (cutoff_date,)
        )
        high_relevance = cursor.fetchone()[0]

        # News by LP
        cursor.execute("""
            SELECT lp_name, COUNT(*) as count
            FROM news_items
            WHERE date >= ?
            GROUP BY lp_name
            ORDER BY count DESC
        """, (cutoff_date,))
        by_lp = dict(cursor.fetchall())

        # News by category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM news_items
            WHERE date >= ? AND category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """, (cutoff_date,))
        by_category = dict(cursor.fetchall())

        return {
            "total_news": total_news,
            "high_relevance_news": high_relevance,
            "by_lp": by_lp,
            "by_category": by_category,
            "period_days": days
        }

    def save_collection_run(self, run: CollectionRun) -> bool:
        """Save a collection run record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO collection_runs (
                    id, start_time, end_time, status,
                    lps_processed, news_collected, errors
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run.id,
                run.start_time,
                run.end_time,
                run.status,
                json.dumps(run.lps_processed),
                run.news_collected,
                json.dumps(run.errors)
            ))

            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Error saving collection run: {e}")
            return False

    def _row_to_news_item(self, row: sqlite3.Row) -> NewsItem:
        """Convert database row to NewsItem"""
        return NewsItem(
            id=row['id'],
            lp_name=row['lp_name'],
            title=row['title'],
            url=row['url'],
            date=row['date'],
            collected_at=row['collected_at'],
            content=row['content'],
            content_summary=row['content_summary'],
            category=row['category'],
            korea_relevance_score=row['korea_relevance_score'],
            key_points=json.loads(row['key_points']) if row['key_points'] else [],
            action_items=json.loads(row['action_items']) if row['action_items'] else [],
            amount=row['amount'],
            currency=row['currency'],
            sectors=json.loads(row['sectors']) if row['sectors'] else [],
            regions=json.loads(row['regions']) if row['regions'] else [],
            tags=json.loads(row['tags']) if row['tags'] else [],
            source=row['source'],
            language=row['language']
        )

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
