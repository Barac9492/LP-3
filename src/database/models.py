"""
Database models for LP monitoring system
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class NewsItem:
    """Represents a news article about an LP institution"""

    # Required fields
    lp_name: str
    title: str
    url: str
    date: str  # ISO format YYYY-MM-DD

    # Auto-generated
    id: Optional[str] = None  # Will be generated as hash of URL
    collected_at: Optional[str] = None  # When the news was collected

    # Content
    content: Optional[str] = None
    content_summary: Optional[str] = None

    # Classification
    category: Optional[str] = None  # 신규_출자_약정, 전략_변화, etc.

    # Scoring
    korea_relevance_score: int = 0  # 1-5

    # Analysis results
    key_points: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)

    # Financial details
    amount: Optional[float] = None  # USD
    currency: str = "USD"

    # Tags
    sectors: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Metadata
    source: Optional[str] = None
    language: str = "en"

    def __post_init__(self):
        """Generate ID and timestamp if not provided"""
        if self.id is None:
            # Generate ID from URL hash
            import hashlib
            self.id = hashlib.md5(self.url.encode()).hexdigest()

        if self.collected_at is None:
            self.collected_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> 'NewsItem':
        """Create NewsItem from dictionary"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'NewsItem':
        """Create NewsItem from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def is_high_relevance(self) -> bool:
        """Check if this news has high Korea relevance"""
        return self.korea_relevance_score >= 4

    def is_large_commitment(self, threshold: float = 100_000_000) -> bool:
        """Check if this is a large commitment"""
        return self.amount is not None and self.amount >= threshold


@dataclass
class LPProfile:
    """Represents an LP institution profile"""

    name: str
    full_name: str
    country: str
    aum: float  # Assets under management in USD
    pe_allocation_pct: float
    focus_regions: List[str]
    website: str
    korea_interest: str  # low, medium, high, very_high
    search_keywords: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'LPProfile':
        """Create LPProfile from dictionary"""
        return cls(name=name, **data)


@dataclass
class CollectionRun:
    """Represents a news collection run"""

    id: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"  # running, completed, failed
    lps_processed: List[str] = field(default_factory=list)
    news_collected: int = 0
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'CollectionRun':
        """Create CollectionRun from dictionary"""
        return cls(**data)
