import time
import random
from playwright.sync_api import sync_playwright
from database.sheets_client import sheets_client
from config.logger import logger
from scrapers.web_enricher import web_enricher

class GoogleMapsScraper:
    def scrape_by_sector(self, sector):
        logger.info(f"Starting Google Maps scrape for sector: {sector}")
        queries = [f"entreprises {sector} Tunisie", f"{sector} Tunis"]
        
        leads = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            for query in queries:
                try:
                    logger.info(f"Navigating to maps search: {query}")
                    page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
                    time.sleep(random.uniform(3, 8))
                    
                    try:
                        page.locator("button:has-text('Accept all')").click(timeout=3000)
                    except:
                        pass
                    
                    elements = page.locator(".Nv2PK").all()
                    logger.info(f"Found {len(elements[:10])} results for {query}")
                    
                    for el in elements[:10]:
                        try:
                            name = el.locator(".qBF1Pd").inner_text() if el.locator(".qBF1Pd").count() > 0 else "Unknown"
                            website_el = el.locator("a[href^='http']").first
                            website_url = website_el.get_attribute("href") if website_el else None
                            
                            logger.info(f"Processing Maps lead: {name}")
                            
                            if not sheets_client.lead_exists(phone=name):
                                lead = {
                                    "id": f"gm_{str(random.randint(100000, 999999))}",
                                    "company": name,
                                    "source": "google_maps",
                                    "sector": sector,
                                    "status": "pending_enrichment",
                                    "notes": f"WEBSITE: {website_url}" if website_url else ""
                                }
                                
                                leads.append(lead)
                                sheets_client.add_lead(lead)
                                logger.info(f"Saved raw lead: {name} to pipeline.")
                            else:
                                logger.info(f"Lead {name} already exists. Skipping.")
                        except Exception as e:
                            logger.error(f"Error extracting gm element: {e}")
                except Exception as e:
                    logger.error(f"Page load error for {query}: {e}")
                    
            browser.close()
            
        logger.info(f"Finished Google Maps scrape for {sector}. Found {len(leads)} leads.")
        return leads

google_maps_scraper = GoogleMapsScraper()
