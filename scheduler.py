from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scrapers.ai_models_scraper import run_spider
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_scheduler():
    """Initialize the scheduler for periodic model updates"""
    scheduler = BackgroundScheduler()
    
    # Schedule the scraper to run every 5 minutes
    scheduler.add_job(
        func=run_spider,
        trigger=IntervalTrigger(minutes=5),
        id='scrape_ai_models',
        name='Scrape AI Models from various sources',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - AI Models will be updated every 5 minutes")
