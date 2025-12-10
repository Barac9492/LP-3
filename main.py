#!/usr/bin/env python3
"""
LP Investment Monitoring System - Main Entry Point
Orchestrates news collection, analysis, and reporting
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
import yaml

from src.collectors.lp_profiles import LPProfileManager
from src.collectors.search_queries import SearchQueryGenerator
from src.collectors.news_collector import NewsCollector
from src.analyzers.classifier import NewsClassifier
from src.analyzers.scorer import KoreaRelevanceScorer
from src.analyzers.summarizer import NewsSummarizer
from src.reporters.weekly_report import WeeklyReportGenerator
from src.reporters.monthly_report import MonthlyReportGenerator
from src.reporters.alert_system import AlertSystem
from src.database.db_manager import DatabaseManager
from src.database.models import CollectionRun


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'lp_monitor.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def collect_and_analyze(
    lp_names: list,
    days: int,
    config: dict,
    db: DatabaseManager,
    use_ai: bool = True
) -> list:
    """Collect and analyze news for specified LPs"""
    logger = logging.getLogger(__name__)

    # Initialize components
    logger.info("Initializing components...")
    lp_manager = LPProfileManager()
    query_generator = SearchQueryGenerator()
    collector = NewsCollector(lp_manager, query_generator)

    # Initialize analyzers
    if use_ai:
        classifier = NewsClassifier(
            api_provider=config.get('api', {}).get('provider', 'openai'),
            model=config.get('api', {}).get('openai', {}).get('model', 'gpt-4')
        )
        summarizer = NewsSummarizer(
            api_provider=config.get('api', {}).get('provider', 'openai'),
            model=config.get('api', {}).get('openai', {}).get('model', 'gpt-4')
        )
    else:
        classifier = None
        summarizer = None

    scorer = KoreaRelevanceScorer(config)

    # Create collection run
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    collection_run = CollectionRun(
        id=run_id,
        start_time=datetime.now().isoformat(),
        status='running'
    )

    all_news = []

    try:
        # Collect news
        print(f"\n🔍 LP 뉴스 모니터링 시작... (최근 {days}일)")
        print("=" * 60)

        for lp_name in lp_names:
            print(f"\n📰 {lp_name} 뉴스 수집 중...")

            news_items = collector.collect_news_for_lp(
                lp_name,
                days=days,
                max_results=config.get('search', {}).get('max_results_per_lp', 10)
            )

            if news_items:
                print(f"✅ {lp_name}: {len(news_items)}개 뉴스 수집")

                # Analyze news
                for news in news_items:
                    # Classify
                    if classifier:
                        try:
                            news = classifier.classify(news)
                        except Exception as e:
                            logger.error(f"Error classifying news: {e}")

                    # Score
                    news = scorer.score(news)

                    # Save to database
                    db.save_news_item(news)

                all_news.extend(news_items)
                collection_run.lps_processed.append(lp_name)
            else:
                print(f"⚠️  {lp_name}: 뉴스 없음")

        collection_run.news_collected = len(all_news)
        collection_run.end_time = datetime.now().isoformat()
        collection_run.status = 'completed'

        print("\n" + "=" * 60)
        print(f"📊 총 {len(all_news)}개 뉴스 분석 완료")

        # Statistics
        high_relevance = [n for n in all_news if n.korea_relevance_score >= 4]
        if high_relevance:
            print(f"🔥 한국 관련 고득점 시그널 {len(high_relevance)}건 발견!")

        return all_news

    except Exception as e:
        logger.error(f"Error during collection: {e}")
        collection_run.status = 'failed'
        collection_run.errors.append(str(e))
        raise

    finally:
        db.save_collection_run(collection_run)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LP Investment Monitoring System'
    )

    parser.add_argument(
        '--mode',
        choices=['instant', 'weekly', 'monthly', 'test'],
        default='instant',
        help='Execution mode'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (for instant mode)'
    )

    parser.add_argument(
        '--lps',
        nargs='+',
        help='Specific LP names to monitor (default: all tier1)'
    )

    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI analysis (use rule-based classification)'
    )

    parser.add_argument(
        '--report',
        choices=['weekly', 'monthly', 'both'],
        help='Generate report'
    )

    parser.add_argument(
        '--alert',
        action='store_true',
        help='Send alerts for high-relevance news'
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to config file'
    )

    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    logger.info("Starting LP Monitoring System")

    try:
        # Load configuration
        config = load_config(args.config)

        # Initialize database
        db = DatabaseManager(config['database']['path'])

        # Determine which LPs to monitor
        if args.lps:
            lp_names = args.lps
        else:
            lp_names = config['lp_tiers']['tier1']

        # Execute based on mode
        if args.mode == 'instant':
            # Collect and analyze news
            all_news = collect_and_analyze(
                lp_names,
                args.days,
                config,
                db,
                use_ai=not args.no_ai
            )

            # Generate report if requested
            if args.report:
                print(f"\n📄 리포트 생성 중...")

                if args.report in ['weekly', 'both']:
                    report_gen = WeeklyReportGenerator(db)
                    report = report_gen.generate_report()
                    filepath = report_gen.save_report(report)
                    print(f"✅ 주간 리포트 저장: {filepath}")

                if args.report in ['monthly', 'both']:
                    report_gen = MonthlyReportGenerator(db)
                    report = report_gen.generate_report()
                    filepath = report_gen.save_report(report)
                    print(f"✅ 월간 리포트 저장: {filepath}")

            # Send alerts if requested
            if args.alert:
                print(f"\n🔔 알림 발송 중...")
                alert_system = AlertSystem(config)

                high_relevance = [n for n in all_news if n.korea_relevance_score >= 4]
                if high_relevance:
                    alert_system.send_batch_alert(
                        high_relevance,
                        subject=f"LP 뉴스 고득점 시그널 {len(high_relevance)}건"
                    )
                    print(f"✅ 알림 발송 완료")
                else:
                    print("ℹ️  고득점 시그널 없음 (알림 미발송)")

        elif args.mode == 'weekly':
            # Generate weekly report only
            print(f"\n📄 주간 리포트 생성 중...")
            report_gen = WeeklyReportGenerator(db)
            report = report_gen.generate_report()
            filepath = report_gen.save_report(report)
            print(f"✅ 주간 리포트 저장: {filepath}")

        elif args.mode == 'monthly':
            # Generate monthly report only
            print(f"\n📄 월간 리포트 생성 중...")
            report_gen = MonthlyReportGenerator(db)
            report = report_gen.generate_report()
            filepath = report_gen.save_report(report)
            print(f"✅ 월간 리포트 저장: {filepath}")

        elif args.mode == 'test':
            # Test mode - verify configuration
            print("\n🧪 테스트 모드")
            print("=" * 60)

            print("\n1. 설정 파일 확인...")
            print(f"   ✅ Config loaded: {len(config)} sections")

            print("\n2. LP 프로필 확인...")
            lp_manager = LPProfileManager()
            print(f"   ✅ Loaded {len(lp_manager.profiles)} LP profiles")

            print("\n3. 데이터베이스 확인...")
            stats = db.get_statistics(days=30)
            print(f"   ✅ Total news in DB (30 days): {stats['total_news']}")

            print("\n4. 알림 시스템 테스트...")
            alert_system = AlertSystem(config)
            if alert_system.email_enabled or alert_system.slack_enabled:
                print("   ⚠️  Alert test available. Run with --alert flag to test.")
            else:
                print("   ℹ️  Alerts not configured (email and slack disabled)")

            print("\n✅ 시스템 테스트 완료")

        print("\n✅ 완료!")

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단됨")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == '__main__':
    main()
