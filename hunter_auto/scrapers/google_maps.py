import time
import random
from playwright.sync_api import sync_playwright
from database.sheets_client import sheets_client
from config.logger import logger
from scrapers.web_enricher import web_enricher

class GoogleMapsScraper:
    def scrape_by_sector(self, sector, limit=10, sync_mode=False, city='Tunis'):
        logger.info(f"Starting Google Maps scrape for sector: {sector} in {city} with limit: {limit}")
        queries = [f"entreprises {sector} {city}", f"{sector} {city}"]
        
        leads = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            for query in queries:
                if len(leads) >= limit:
                    break
                    
                try:
                    logger.info(f"Navigating to maps search: {query}")
                    page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
                    time.sleep(random.uniform(3, 8))
                    
                    try:
                        page.locator("button:has-text('Accept all')").click(timeout=3000)
                    except:
                        pass
                    
                    # Scroll feed to load more results
                    feed_selector = "div[role='feed']"
                    page.wait_for_selector(feed_selector, timeout=10000)
                    
                    elements_count = 0
                    scroll_attempts = 0
                    while elements_count < limit and scroll_attempts < 10:
                        page.locator(feed_selector).evaluate("el => el.scrollBy(0, 5000)")
                        time.sleep(random.uniform(2, 4))
                        new_count = page.locator(".Nv2PK").count()
                        if new_count == elements_count:
                            scroll_attempts += 1
                        else:
                            scroll_attempts = 0
                            elements_count = new_count
                            
                    elements = page.locator(".Nv2PK").all()
                    logger.info(f"Found {len(elements)} results for {query} (Processing up to {limit})")
                    
                    for el in elements[:limit]:
                        try:
                            name = el.locator(".qBF1Pd").inner_text() if el.locator(".qBF1Pd").count() > 0 else "Unknown"
                            website_el = el.locator("a[href^='http']").first
                            website_url = website_el.get_attribute("href") if website_el else None
                            
                            logger.info(f"Processing Maps lead: {name}")
                            
                            if not sheets_client.lead_exists(company=name) or sync_mode:
                                lead = {
                                    "id": f"gm_{str(random.randint(100000, 999999))}",
                                    "name": "",
                                    "title": "",
                                    "company": name,
                                    "linkedin_url": "",
                                    "source": "google_maps",
                                    "sector": sector,
                                    "status": "pending_enrichment",
                                    "notes": f"WEBSITE: {website_url}" if website_url else ""
                                }
                                
                                logger.info(f"Checking contact options for {name}...")
                                enrichment = web_enricher.enrich_lead(name, website_url)
                                
                                if enrichment.get("emails") or enrichment.get("phones"):
                                    lead["email"] = enrichment["emails"][0] if enrichment.get("emails") else ""
                                    lead["phone"] = enrichment["phones"][0] if enrichment.get("phones") else ""
                                    logger.info(f"Contacts found for {name}.")
                                else:
                                    lead["status"] = "skipped"
                                    lead["notes"] += " | No contact options found initially"
                                    logger.info(f"No contact options found initially for {name}, saving as skipped.")
                                
                                leads.append(lead)
                                if not sync_mode:
                                    sheets_client.add_lead(lead)
                                logger.info(f"Saved lead: {name} to pipeline.")
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
