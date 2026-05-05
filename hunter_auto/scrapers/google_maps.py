import time
import random
from playwright.sync_api import sync_playwright
from database.sheets_client import sheets_client

class GoogleMapsScraper:
    def scrape_by_sector(self, sector):
        print(f"Starting Google Maps scrape for sector: {sector}")
        queries = [f"entreprises {sector} Tunisie", f"{sector} Tunis"]
        
        leads = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            for query in queries:
                try:
                    page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
                    time.sleep(random.uniform(3, 8))
                    
                    try:
                        page.locator("button:has-text('Accept all')").click(timeout=3000)
                    except:
                        pass
                    
                    elements = page.locator(".Nv2PK").all()
                    for el in elements[:10]:
                        try:
                            # Basic extraction
                            name = el.locator(".qBF1Pd").inner_text() if el.locator(".qBF1Pd").count() > 0 else "Unknown"
                            
                            if not sheets_client.lead_exists(phone=name):
                                lead = {
                                    "id": f"gm_{str(random.randint(100000, 999999))}",
                                    "company": name,
                                    "source": "google_maps",
                                    "sector": sector,
                                    "status": "pending"
                                }
                                leads.append(lead)
                                sheets_client.add_lead(lead)
                        except Exception as e:
                            print(f"Error extracting gm element: {e}")
                except Exception as e:
                    print(f"Page load error: {e}")
                    
            browser.close()
            
        print(f"Finished Google Maps scrape for {sector}. Found {len(leads)} leads.")
        return leads

google_maps_scraper = GoogleMapsScraper()
