from apscheduler.schedulers.background import BackgroundScheduler
import time
from scrapers.google_maps import google_maps_scraper
from scrapers.linkedin_scraper import linkedin_scraper
from outreach.router import outreach_router
import config.settings as app_settings

class AutomationAgent:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=app_settings.TIMEZONE)

    def scrape_job(self):
        from config.logger import logger
        logger.info("[Agent] Running scrape_job (Maps & LinkedIn)...")
        for sector in app_settings.TARGET_SECTORS:
            google_maps_scraper.scrape_by_sector(sector)
            linkedin_scraper.scrape_decision_makers(sector)

    def enrich_job(self):
        from config.logger import logger
        logger.info("[Agent] Running enrich_job (Data Enrichment & AI Scoring)...")
        # 1. Process Pending Enrichment leads (Scraping Layer -> Local AI Layer)
        from ai.enrichment_engine import enrichment_engine
        enrichment_engine.process_pending_enrichment()

    def outreach_job(self):
        from config.logger import logger
        logger.info("[Agent] Running outreach_job (Cold Call MatchMaker)...")
        limit = app_settings.OUTREACH_DAILY_LIMIT
        outreach_router.process_pending_leads(batch_size=limit)

    def start(self):
        # 1. Scraping Layer (24/7)
        self.scheduler.add_job(self.scrape_job, 'interval', hours=app_settings.SCRAPE_INTERVAL_HOURS, id='scrape_job')
        
        # 2. Enrichment & AI Layer (Every 3 hours)
        self.scheduler.add_job(self.enrich_job, 'interval', hours=3, id='enrich_job')
        
        # 3. Outreach Paths (Scheduler Daytime only: 08:00-18:00 Tunis time)
        self.scheduler.add_job(self.outreach_job, 'cron', day_of_week='mon-fri', hour='8-18', minute='30', id='outreach_job')
        
        self.scheduler.start()
        print("Scheduler started.")

    def update_jobs(self):
        self.scheduler.reschedule_job('scrape_job', trigger='interval', hours=app_settings.SCRAPE_INTERVAL_HOURS)
        print("Scheduler jobs updated.")

    def pause(self):
        self.scheduler.pause()
        print("Scheduler paused.")

    def resume(self):
        self.scheduler.resume()
        print("Scheduler resumed.")

    def get_status(self):
        return {
            "is_running": self.scheduler.state == 1,
            "jobs": [{"id": j.id, "next_run_time": str(j.next_run_time)} for j in self.scheduler.get_jobs()]
        }

agent = AutomationAgent()
