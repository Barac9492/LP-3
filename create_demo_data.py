#!/usr/bin/env python3
"""
Create demo data for LP Monitoring Dashboard
"""
from datetime import datetime, timedelta
from src.database.db_manager import DatabaseManager
from src.database.models import NewsItem

def create_demo_data():
    """Create sample news data"""
    db = DatabaseManager()

    demo_news = [
        NewsItem(
            lp_name="GIC",
            title="GIC increases Asia-Pacific venture capital allocation by $2B",
            url="https://example.com/gic-asia-vc",
            date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            content="GIC announced a significant increase in venture capital allocation for the Asia-Pacific region, focusing on AI and semiconductor startups.",
            content_summary="GIC commits $2B to Asia-Pacific VC, with focus on AI and semiconductor sectors. This represents a 30% increase from previous year.",
            category="신규_출자_약정",
            korea_relevance_score=5,
            key_points=[
                "Total commitment: $2 billion",
                "Focus sectors: AI, semiconductor, biotech",
                "Target markets: South Korea, Singapore, Taiwan",
                "Timeline: 2024-2027"
            ],
            action_items=[
                "Contact GIC investment team",
                "Prepare Korean AI portfolio overview",
                "Identify co-investment opportunities"
            ],
            amount=2_000_000_000,
            sectors=["AI", "semiconductor", "biotech"],
            regions=["Asia", "Korea"],
            tags=["korea_direct", "large_commitment"],
            source="web_search"
        ),
        NewsItem(
            lp_name="Temasek",
            title="Temasek establishes $500M Korea Innovation Fund",
            url="https://example.com/temasek-korea",
            date=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            content="Temasek Holdings announces new dedicated fund for Korean startups focusing on deep tech and green technology.",
            content_summary="Temasek launches $500M Korea-focused innovation fund targeting deep tech and green technology startups.",
            category="한국_관련",
            korea_relevance_score=5,
            key_points=[
                "Fund size: $500 million",
                "Focus: Deep tech, green technology",
                "Investment stage: Series B and later",
                "First close expected Q1 2025"
            ],
            amount=500_000_000,
            sectors=["deep tech", "cleantech"],
            regions=["Korea"],
            tags=["korea_direct"],
            source="web_search"
        ),
        NewsItem(
            lp_name="CPPIB",
            title="CPP Investments expands emerging markets strategy",
            url="https://example.com/cppib-emerging",
            date=(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
            content="Canada Pension Plan Investment Board announces expansion of emerging markets venture capital strategy.",
            content_summary="CPPIB increases emerging markets allocation, with particular interest in Asian technology sectors.",
            category="전략_변화",
            korea_relevance_score=4,
            key_points=[
                "10% increase in emerging markets allocation",
                "Focus on Asia technology sector",
                "Seeking new GP partnerships"
            ],
            sectors=["technology", "fintech"],
            regions=["Asia", "emerging markets"],
            tags=["asia_focus"],
            source="web_search"
        ),
        NewsItem(
            lp_name="NPS",
            title="NPS reports 12.5% return on alternative investments",
            url="https://example.com/nps-returns",
            date=(datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
            content="National Pension Service announces strong performance in alternative investment portfolio.",
            content_summary="NPS achieves 12.5% return on alternatives, plans to increase VC allocation in 2025.",
            category="성과_발표",
            korea_relevance_score=5,
            key_points=[
                "12.5% return on alternatives portfolio",
                "Plan to increase VC allocation by 2%",
                "Focus on domestic deep tech startups"
            ],
            sectors=["venture capital", "private equity"],
            regions=["Korea"],
            tags=["korea_direct"],
            source="web_search"
        ),
        NewsItem(
            lp_name="CalPERS",
            title="CalPERS appoints new Head of Private Equity",
            url="https://example.com/calpers-cio",
            date=(datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            content="CalPERS announces new leadership for private equity division.",
            content_summary="CalPERS appoints veteran investor as new Head of Private Equity, signaling potential strategy shift.",
            category="인사_변동",
            korea_relevance_score=2,
            key_points=[
                "New PE head has Asia investment background",
                "Previous role at major Asian pension fund",
                "May signal increased Asia focus"
            ],
            sectors=["private equity"],
            tags=["personnel"],
            source="web_search"
        ),
        NewsItem(
            lp_name="GIC",
            title="GIC commits $300M to semiconductor fund",
            url="https://example.com/gic-semiconductor",
            date=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            content="GIC invests in specialized semiconductor venture fund.",
            content_summary="GIC commits $300M to semiconductor-focused VC fund targeting Asian chip startups.",
            category="신규_출자_약정",
            korea_relevance_score=5,
            amount=300_000_000,
            sectors=["semiconductor"],
            regions=["Asia"],
            tags=["korea_direct", "relevant_sector"],
            source="web_search"
        ),
        NewsItem(
            lp_name="ADIA",
            title="ADIA increases technology sector allocation",
            url="https://example.com/adia-tech",
            date=(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
            content="Abu Dhabi Investment Authority announces increased focus on technology investments.",
            content_summary="ADIA boosts technology allocation, with interest in AI and cloud infrastructure.",
            category="전략_변화",
            korea_relevance_score=3,
            sectors=["AI", "cloud"],
            tags=["relevant_sector"],
            source="web_search"
        ),
        NewsItem(
            lp_name="Ontario Teachers",
            title="Ontario Teachers completes $1.2B venture fund commitment",
            url="https://example.com/otpp-vc",
            date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            content="Ontario Teachers' Pension Plan makes significant VC fund commitment.",
            content_summary="OTPP commits $1.2B to global venture funds, including Asia-focused managers.",
            category="신규_출자_약정",
            korea_relevance_score=3,
            amount=1_200_000_000,
            sectors=["venture capital"],
            regions=["Global"],
            tags=["large_commitment"],
            source="web_search"
        )
    ]

    print("📊 Creating demo data...")
    for news in demo_news:
        db.save_news_item(news)
        print(f"✅ Added: {news.lp_name} - {news.title[:50]}...")

    print(f"\n✅ Created {len(demo_news)} demo news items")
    print("\n📈 Statistics:")
    stats = db.get_statistics(days=7)
    print(f"  - Total news: {stats['total_news']}")
    print(f"  - High relevance: {stats['high_relevance_news']}")
    print(f"  - Active LPs: {len(stats['by_lp'])}")

if __name__ == "__main__":
    create_demo_data()
