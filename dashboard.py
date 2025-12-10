#!/usr/bin/env python3
"""
LP Investment Monitoring System - Web Dashboard
Interactive dashboard for monitoring LP investment activities
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager
from src.collectors.lp_profiles import LPProfileManager
from src.reporters.weekly_report import WeeklyReportGenerator
from src.reporters.monthly_report import MonthlyReportGenerator


# Page configuration
st.set_page_config(
    page_title="LP Investment Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .news-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .high-score {
        background: #fff3cd;
        border-left-color: #ffc107 !important;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db():
    """Get database connection"""
    return DatabaseManager()


@st.cache_resource
def get_lp_manager():
    """Get LP profile manager"""
    return LPProfileManager()


def format_amount(amount):
    """Format currency amount"""
    if amount is None:
        return "N/A"
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    else:
        return f"${amount:,.0f}"


def render_header():
    """Render page header"""
    st.markdown('<h1 class="main-header">📊 LP Investment Monitor</h1>', unsafe_allow_html=True)
    st.markdown("---")


def render_overview_metrics(db):
    """Render overview metrics"""
    col1, col2, col3, col4 = st.columns(4)

    # Get statistics
    stats_7d = db.get_statistics(days=7)
    stats_30d = db.get_statistics(days=30)

    with col1:
        st.metric(
            label="📰 Total News (7d)",
            value=stats_7d['total_news'],
            delta=f"{stats_7d['total_news'] - stats_30d['total_news'] + stats_7d['total_news']} vs 30d"
        )

    with col2:
        st.metric(
            label="🔥 High Relevance (7d)",
            value=stats_7d['high_relevance_news'],
            delta=f"{stats_7d['high_relevance_news']} signals"
        )

    with col3:
        active_lps = len(stats_7d['by_lp'])
        st.metric(
            label="🏢 Active LPs",
            value=active_lps,
            delta=f"{active_lps} institutions"
        )

    with col4:
        categories = len(stats_7d['by_category'])
        st.metric(
            label="📂 Categories",
            value=categories,
            delta=f"{categories} types"
        )


def render_news_feed(db, days=7, min_score=0):
    """Render news feed"""
    st.subheader("📰 Recent News")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        days = st.selectbox("Time Period", [1, 3, 7, 14, 30], index=2)

    with col2:
        min_score = st.slider("Minimum Score", 1, 5, 0)

    with col3:
        lp_manager = get_lp_manager()
        lp_filter = st.multiselect(
            "Filter by LP",
            options=["All"] + lp_manager.get_lp_names(),
            default=["All"]
        )

    # Get news
    news_items = db.get_recent_news(days=days, min_score=min_score)

    # Filter by LP if selected
    if "All" not in lp_filter and lp_filter:
        news_items = [n for n in news_items if n.lp_name in lp_filter]

    st.write(f"Found **{len(news_items)}** news items")

    # Display news
    for news in news_items[:20]:  # Limit to 20
        score_stars = "⭐" * news.korea_relevance_score
        is_high_score = news.korea_relevance_score >= 4

        card_class = "news-card high-score" if is_high_score else "news-card"

        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{news.lp_name}** - {news.title}")
            if news.content_summary:
                st.caption(news.content_summary[:200] + "...")

        with col2:
            st.write(f"Score: {score_stars}")
            st.caption(f"📅 {news.date}")
            if news.category:
                st.caption(f"📂 {news.category}")

        if news.key_points:
            with st.expander("📌 Key Points"):
                for point in news.key_points:
                    st.write(f"• {point}")

        if news.url:
            st.markdown(f"[🔗 Read Full Article]({news.url})")

        st.markdown('</div>', unsafe_allow_html=True)


def render_lp_activity(db):
    """Render LP activity overview"""
    st.subheader("🏢 LP Activity Overview")

    days = st.selectbox("Period", [7, 14, 30], key="lp_activity_days")

    # Get statistics
    stats = db.get_statistics(days=days)

    if not stats['by_lp']:
        st.info("No data available for this period")
        return

    # Create DataFrame
    lp_data = []
    for lp_name, count in stats['by_lp'].items():
        # Get high score count
        news_items = db.get_news_by_lp(lp_name, days=days, min_score=0)
        high_score = sum(1 for n in news_items if n.korea_relevance_score >= 4)
        avg_score = sum(n.korea_relevance_score for n in news_items) / len(news_items) if news_items else 0

        lp_data.append({
            'LP': lp_name,
            'Total News': count,
            'High Score (4-5)': high_score,
            'Avg Score': round(avg_score, 1)
        })

    df = pd.DataFrame(lp_data).sort_values('Total News', ascending=False)

    # Display chart
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df,
            x='LP',
            y='Total News',
            title=f'News Count by LP (Last {days} days)',
            color='Avg Score',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            df,
            values='Total News',
            names='LP',
            title='News Distribution by LP'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Data table
    st.dataframe(df, use_container_width=True)


def render_category_breakdown(db):
    """Render category breakdown"""
    st.subheader("📂 Category Breakdown")

    days = st.selectbox("Period", [7, 14, 30], key="category_days")

    stats = db.get_statistics(days=days)

    if not stats['by_category']:
        st.info("No categorized news available")
        return

    # Create DataFrame
    cat_data = [
        {'Category': cat, 'Count': count}
        for cat, count in stats['by_category'].items()
    ]
    df = pd.DataFrame(cat_data).sort_values('Count', ascending=False)

    # Chart
    fig = px.bar(
        df,
        x='Category',
        y='Count',
        title=f'News by Category (Last {days} days)',
        color='Count',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_high_signals(db):
    """Render high relevance signals"""
    st.subheader("🔥 High Relevance Signals")

    days = st.selectbox("Period", [7, 14, 30], key="signals_days")

    high_news = db.get_high_relevance_news(days=days, threshold=4)

    if not high_news:
        st.info(f"No high relevance signals in the last {days} days")
        return

    st.write(f"Found **{len(high_news)}** high-relevance signals")

    for news in high_news[:10]:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"**{news.lp_name}**: {news.title}")

            with col2:
                st.write("⭐" * news.korea_relevance_score)

            with col3:
                st.caption(news.date)

            if news.content_summary:
                st.write(news.content_summary)

            if news.amount:
                st.write(f"💰 Amount: {format_amount(news.amount)}")

            if news.sectors:
                st.write(f"🎯 Sectors: {', '.join(news.sectors)}")

            if news.url:
                st.markdown(f"[Read More]({news.url})")

            st.markdown("---")


def render_actions():
    """Render action buttons"""
    st.subheader("⚡ Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Collect News Now", use_container_width=True):
            with st.spinner("Collecting news..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "main.py", "--mode", "instant", "--days", "3", "--no-ai"],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        st.success("✅ News collection completed!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    with col2:
        if st.button("📄 Generate Weekly Report", use_container_width=True):
            with st.spinner("Generating report..."):
                try:
                    db = get_db()
                    report_gen = WeeklyReportGenerator(db)
                    report = report_gen.generate_report()
                    filepath = report_gen.save_report(report)

                    st.success(f"✅ Report saved to: {filepath}")

                    # Offer download
                    with open(filepath, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="⬇️ Download Report",
                            data=f.read(),
                            file_name=Path(filepath).name,
                            mime="text/markdown"
                        )
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    with col3:
        if st.button("📊 Generate Monthly Report", use_container_width=True):
            with st.spinner("Generating report..."):
                try:
                    db = get_db()
                    report_gen = MonthlyReportGenerator(db)
                    report = report_gen.generate_report()
                    filepath = report_gen.save_report(report)

                    st.success(f"✅ Report saved to: {filepath}")

                    with open(filepath, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="⬇️ Download Report",
                            data=f.read(),
                            file_name=Path(filepath).name,
                            mime="text/markdown"
                        )
                except Exception as e:
                    st.error(f"❌ Error: {e}")


def render_lp_profiles():
    """Render LP profiles"""
    st.subheader("🏢 LP Profiles")

    lp_manager = get_lp_manager()

    # Select LP
    lp_name = st.selectbox(
        "Select LP",
        options=lp_manager.get_lp_names()
    )

    if lp_name:
        profile = lp_manager.get_profile(lp_name)

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Full Name:** {profile.full_name}")
            st.write(f"**Country:** {profile.country}")
            st.write(f"**AUM:** {format_amount(profile.aum)}")
            st.write(f"**PE Allocation:** {profile.pe_allocation_pct}%")

        with col2:
            st.write(f"**Focus Regions:** {', '.join(profile.focus_regions)}")
            st.write(f"**Korea Interest:** {profile.korea_interest}")
            st.write(f"**Website:** {profile.website}")

        st.write("**Search Keywords:**")
        for keyword in profile.search_keywords:
            st.write(f"• {keyword}")


def main():
    """Main dashboard"""
    render_header()

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=LP+Monitor", use_container_width=True)
        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "🏠 Overview",
                "📰 News Feed",
                "🔥 High Signals",
                "🏢 LP Activity",
                "📂 Categories",
                "🏦 LP Profiles",
                "⚡ Actions"
            ]
        )

        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Main content
    db = get_db()

    if page == "🏠 Overview":
        render_overview_metrics(db)
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            render_high_signals(db)
        with col2:
            render_lp_activity(db)

    elif page == "📰 News Feed":
        render_news_feed(db)

    elif page == "🔥 High Signals":
        render_high_signals(db)

    elif page == "🏢 LP Activity":
        render_lp_activity(db)
        st.markdown("---")
        render_category_breakdown(db)

    elif page == "📂 Categories":
        render_category_breakdown(db)

    elif page == "🏦 LP Profiles":
        render_lp_profiles()

    elif page == "⚡ Actions":
        render_actions()


if __name__ == "__main__":
    main()
