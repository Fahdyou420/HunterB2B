import re
import requests
from bs4 import BeautifulSoup
from config.settings import HUNTER_IO_API_KEY
from database.sheets_client import sheets_client
from ai.contact_extractor import contact_extractor

class WebEnricher:
    def enrich_lead(self, company, website_url):
        print(f"Enriching {company} via {website_url}")
        emails = []
        phones = []
        
        # Scrape Website
        if website_url:
            try:
                response = requests.get(website_url, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                # Basic Regex
                found_emails = re.findall(r'[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+', text)
                found_phones = re.findall(r'(?:\+216\s?|00216\s?|216\s?)?[2-9]\d{1}\s?\d{3}\s?\d{3}', text)
                
                emails.extend(found_emails)
                phones.extend(found_phones)
                
                # AI Extraction
                ai_extract = contact_extractor.extract_contact_info(text[:3000])  # limit to 3000 chars
                emails.extend(ai_extract.get('emails', []))
                phones.extend(ai_extract.get('phones', []))
                
            except Exception as e:
                print(f"Failed to scrape {website_url}: {e}")

        # Hunter.io free tier
        if website_url and HUNTER_IO_API_KEY:
            try:
                domain = website_url.replace('http://', '').replace('https://', '').split('/')[0]
                h_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_IO_API_KEY}"
                h_resp = requests.get(h_url).json()
                if h_resp.get('data', {}).get('emails'):
                    for e in h_resp['data']['emails']:
                        emails.append(e['value'])
            except:
                pass
                
        # Deduplicate
        emails = list(set(emails))
        phones = list(set([p.replace(' ', '') for p in phones]))
        
        return {
            "emails": emails,
            "phones": phones
        }

web_enricher = WebEnricher()
