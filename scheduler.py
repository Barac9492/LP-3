#!/usr/bin/env python3
"""
LP Monitoring System Scheduler
Runs news collection and reporting on a schedule
"""
import schedule
import time
import logging
import sys
import subprocess
from datetime import datetime
import yaml
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'scheduler.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_news_collection():
    """Run daily news collection"""
    logger = logging.getLogger(__name__)
    logger.info("Starting scheduled news collection...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "--mode", "instant",
                "--days", "1",
                "--alert"
            ],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )

        if result.returncode == 0:
            logger.info("News collection completed successfully")
        else:
            logger.error(f"News collection failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("News collection timed out")
    except Exception as e:
        logger.error(f"Error running news collection: {e}")


def run_weekly_report():
    """Run weekly report generation"""
    logger = logging.getLogger(__name__)
    logger.info("Starting weekly report generation...")

    try:
        # First collect last 7 days of news
        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "--mode", "instant",
                "--days", "7",
                "--report", "weekly",
                "--alert"
            ],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        if result.returncode == 0:
            logger.info("Weekly report completed successfully")
        else:
            logger.error(f"Weekly report failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("Weekly report timed out")
    except Exception as e:
        logger.error(f"Error running weekly report: {e}")


def run_monthly_report():
    """Run monthly report generation"""
    logger = logging.getLogger(__name__)
    logger.info("Starting monthly report generation...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "main.py",
                "--mode", "monthly"
            ],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        if result.returncode == 0:
            logger.info("Monthly report completed successfully")
        else:
            logger.error(f"Monthly report failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("Monthly report timed out")
    except Exception as e:
        logger.error(f"Error running monthly report: {e}")


def main():
    """Main scheduler loop"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("LP Monitoring Scheduler starting...")

    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Setup schedules
    scheduler_config = config.get('scheduler', {})

    # Daily news collection
    news_time = scheduler_config.get('news_collection', {}).get('time', '09:00')
    schedule.every().day.at(news_time).do(run_news_collection)
    logger.info(f"Scheduled daily news collection at {news_time}")

    # Weekly report
    weekly_config = scheduler_config.get('weekly_report', {})
    weekly_day = weekly_config.get('day', 'Monday')
    weekly_time = weekly_config.get('time', '10:00')

    if weekly_day.lower() == 'monday':
        schedule.every().monday.at(weekly_time).do(run_weekly_report)
    elif weekly_day.lower() == 'tuesday':
        schedule.every().tuesday.at(weekly_time).do(run_weekly_report)
    elif weekly_day.lower() == 'wednesday':
        schedule.every().wednesday.at(weekly_time).do(run_weekly_report)
    elif weekly_day.lower() == 'thursday':
        schedule.every().thursday.at(weekly_time).do(run_weekly_report)
    elif weekly_day.lower() == 'friday':
        schedule.every().friday.at(weekly_time).do(run_weekly_report)

    logger.info(f"Scheduled weekly report on {weekly_day} at {weekly_time}")

    # Monthly report
    monthly_config = scheduler_config.get('monthly_report', {})
    monthly_day = monthly_config.get('day', 1)
    monthly_time = monthly_config.get('time', '10:00')

    # For monthly, we check every day and run on the correct day
    def monthly_check():
        if datetime.now().day == monthly_day:
            run_monthly_report()

    schedule.every().day.at(monthly_time).do(monthly_check)
    logger.info(f"Scheduled monthly report on day {monthly_day} at {monthly_time}")

    print("\n" + "=" * 60)
    print("🕐 LP Monitoring Scheduler Running")
    print("=" * 60)
    print(f"\n📅 Schedule:")
    print(f"  - Daily news collection: {news_time}")
    print(f"  - Weekly report: {weekly_day} at {weekly_time}")
    print(f"  - Monthly report: Day {monthly_day} at {monthly_time}")
    print(f"\n⏰ Next run: {schedule.next_run()}")
    print("\nPress Ctrl+C to stop\n")

    # Run scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        print("\n\n⚠️  Scheduler stopped by user")
        logger.info("Scheduler stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
