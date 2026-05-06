import time
import random
from playwright.sync_api import sync_playwright
from database.sheets_client import sheets_client
from config.logger import logger
from scrapers.web_enricher import web_enricher

class GoogleMapsScraper:
    def scrape_by_sector(self, sector, limit=10, sync_mode=False, city='Tunis'):
        logger.info(f"Starting Google Maps scrape for sector: {sector} in {city} with limit: {limit}")
        business_types = ["Entreprise", "Société", "Agence", "Cabinet", "Boutique", "Fournisseur", "Grossiste", "Service"]
        queries = [f"{bt} {sector} {city}" for bt in business_types]
        queries.extend([f"{sector} {city}", f"meilleur {sector} {city}"])
        
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
                            # Click the element to open the detail pane
                            try:
                                el.locator("a.hfpxzc").click(timeout=5000)
                                time.sleep(random.uniform(2, 4))
                            except:
                                pass
                                
                            name = el.locator(".qBF1Pd").inner_text() if el.locator(".qBF1Pd").count() > 0 else "Unknown"
                            
                            # Now try to extract from detail pane
                            website_url = None
                            try:
                                website_el = page.locator("a[data-item-id='authority']").first
                                if website_el.count() > 0:
                                    website_url = website_el.get_attribute("href")
                            except: pass
                            
                            address = ""
                            try:
                                addr_el = page.locator("button[data-tooltip*='adresse']").first
                                if addr_el.count() > 0:
                                    address = addr_el.inner_text()
                                else:
                                    # Fallback for English language
                                    addr_el = page.locator("button[data-tooltip*='address']").first
                                    if addr_el.count() > 0:
                                        address = addr_el.inner_text()
                            except: pass
                            
                            phone = ""
                            try:
                                phone_el = page.locator("button[data-tooltip*='téléphone']").first
                                if phone_el.count() > 0:
                                    phone = phone_el.inner_text()
                                else:
                                    # Fallback for English language
                                    phone_el = page.locator("button[data-tooltip*='phone']").first
                                    if phone_el.count() > 0:
                                        phone = phone_el.inner_text()
                            except: pass
                            
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
                                
                                if address:
                                    lead["notes"] += f" | ADDRESS: {address}"

                                logger.info(f"Checking contact options for {name}...")
                                enrichment = web_enricher.enrich_lead(name, website_url)
                                
                                final_emails = enrichment.get("emails", [])
                                final_phones = enrichment.get("phones", [])
                                if phone and phone not in final_phones:
                                    final_phones.append(phone)
                                    
                                if final_emails or final_phones:
                                    lead["email"] = final_emails[0] if final_emails else ""
                                    lead["phone"] = final_phones[0] if final_phones else ""
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
