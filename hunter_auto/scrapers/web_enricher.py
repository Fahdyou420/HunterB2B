import re
import requests
from bs4 import BeautifulSoup
from config.settings import HUNTER_IO_API_KEY
from database.sheets_client import sheets_client
from ai.contact_extractor import contact_extractor
from config.logger import logger

class WebEnricher:
    def enrich_lead(self, company, website_url):
        logger.info(f"Enriching {company} via {website_url}")
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
                
                # Broaden phone regex to catch standard international and local tunisian numbers
                found_phones = re.findall(r'(?:\+?216\s?|00\s?216\s?)?[2-9]\d{1}(?:\s?\d{2}){3}|(?:\+?216\s?)?[97542]\d{7}', text)
                
                emails.extend(found_emails)
                phones.extend(found_phones)
                
                # AI Extraction
                ai_extract = contact_extractor.extract_contact_info(text[:3000])  # limit to 3000 chars
                emails.extend(ai_extract.get('emails', []))
                phones.extend(ai_extract.get('phones', []))
                
            except Exception as e:
                logger.error(f"Failed to scrape {website_url}: {e}")

        # Hunter.io free tier
        if website_url and HUNTER_IO_API_KEY:
            try:
                domain = website_url.replace('http://', '').replace('https://', '').split('/')[0]
                h_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_IO_API_KEY}"
                h_resp = requests.get(h_url).json()
                if h_resp.get('data', {}).get('emails'):
                    for e in h_resp['data']['emails']:
                        emails.append(e['value'])
            except Exception as e:
                logger.error(f"Hunter.io error for {website_url}: {e}")
                
        # Deduplicate
        emails = list(set([e.lower() for e in emails if e]))
        phones = list(set([p.replace(' ', '') for p in phones if p]))
        
        logger.info(f"Enrichment results for {company}: Emails: {len(emails)}, Phones: {len(phones)}")
        
        return {
            "emails": emails,
            "phones": phones
        }

web_enricher = WebEnricher()
