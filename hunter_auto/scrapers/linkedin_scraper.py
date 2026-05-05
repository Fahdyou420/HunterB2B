import time
import random
import os
from playwright.sync_api import sync_playwright
from config.settings import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from database.sheets_client import sheets_client

class LinkedinScraper:
    def __init__(self):
        self.session_dir = "sessions"
        os.makedirs(self.session_dir, exist_ok=True)
        
    def _login(self, page):
        page.goto("https://www.linkedin.com/login")
        time.sleep(random.uniform(2, 4))
        if page.locator("input#username").count() > 0:
            page.fill("input#username", LINKEDIN_EMAIL)
            time.sleep(1)
            page.fill("input#password", LINKEDIN_PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
        
    def scrape_decision_makers(self, sector):
        print(f"Scraping LinkedIn for {sector}")
        queries = [f"directeur {sector} Tunisie", f"CEO {sector} Tunisie"]
        leads = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=self.session_dir+"/state.json" if self._has_state() else None)
            page = context.new_page()
            
            try:
                page.goto("https://www.linkedin.com")
                if "login" in page.url or "checkpoint" in page.url:
                    self._login(page)
                    context.storage_state(path=self.session_dir+"/state.json")
                
                for query in queries:
                    search_url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}"
                    page.goto(search_url)
                    time.sleep(random.uniform(4, 7))
                    
                    results = page.locator(".reusable-search__result-container").all()
                    for res in results[:10]:
                        try:
                            name_el = res.locator(".app-aware-link").first
                            name = name_el.inner_text().split("\n")[0]
                            url = "https://www.linkedin.com" + name_el.get_attribute("href").split('?')[0]
                            title = res.locator(".entity-result__primary-subtitle").inner_text() if res.locator(".entity-result__primary-subtitle").count() > 0 else ""
                            
                            if not sheets_client.lead_exists(linkedin_url=url):
                                lead = {
                                    "id": f"li_{str(random.randint(100000, 999999))}",
                                    "name": name,
                                    "title": title,
                                    "company": "",
                                    "linkedin_url": url,
                                    "source": "linkedin",
                                    "sector": sector,
                                    "status": "pending"
                                }
                                leads.append(lead)
                                sheets_client.add_lead(lead)
                        except Exception as e:
                            print("Error extracting LI lead:", e)
            except Exception as e:
                print(f"Linkedin scraper error: {e}")
            finally:
                browser.close()
        return leads
        
    def _has_state(self):
        return os.path.exists(self.session_dir+"/state.json")

linkedin_scraper = LinkedinScraper()
