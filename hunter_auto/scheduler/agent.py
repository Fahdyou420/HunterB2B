from apscheduler.schedulers.background import BackgroundScheduler
import time
from config.settings import TIMEZONE, SCRAPE_INTERVAL_HOURS, TARGET_SECTORS
from scrapers.google_maps import google_maps_scraper
from scrapers.linkedin_scraper import linkedin_scraper
from outreach.router import outreach_router

class AutomationAgent:
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=TIMEZONE)

    def scrape_job(self):
        print("Running scrape_job...")
        for sector in TARGET_SECTORS:
            google_maps_scraper.scrape_by_sector(sector)

    def enrich_job(self):
        print("Running enrich_job...")
        for sector in TARGET_SECTORS:
            linkedin_scraper.scrape_decision_makers(sector)

    def outreach_job(self):
        print("Running outreach_job...")
        outreach_router.process_pending_leads(batch_size=10)

    def start(self):
        self.scheduler.add_job(self.scrape_job, 'interval', hours=SCRAPE_INTERVAL_HOURS, id='scrape_job')
        self.scheduler.add_job(self.enrich_job, 'interval', hours=4, id='enrich_job')
        self.scheduler.add_job(self.outreach_job, 'cron', hour='8,10,14,16', id='outreach_job')
        self.scheduler.start()
        print("Scheduler started.")

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
