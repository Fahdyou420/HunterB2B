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
                found_phones = re.findall(r'\b(?:\+?216[-.\s]?|00[-.\s]?216[-.\s]?)?[234579]\d(?:[-.\s]?\d{2}){3}\b|\b(?:\+?216[-.\s]?|00[-.\s]?216[-.\s]?)?[234579]\d{7}\b', text)
                
                emails.extend(found_emails)
                phones.extend(found_phones)
                
                # AI Extraction
                ai_extract = contact_extractor.extract_contact_info(text[:3000])  # limit to 3000 chars
                emails.extend(ai_extract.get('emails', []))
                phones.extend(ai_extract.get('phones', []))
                
            except Exception as e:
                logger.error(f"Failed to scrape {website_url}: {e}")

        # Hunter.io free tier (Optional)
        if website_url and HUNTER_IO_API_KEY:
            try:
                logger.info(f"Using Hunter.io fallback for {website_url}")
                domain = website_url.replace('http://', '').replace('https://', '').split('/')[0]
                h_url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_IO_API_KEY}"
                h_resp = requests.get(h_url).json()
                if h_resp.get('data', {}).get('emails'):
                    for e in h_resp['data']['emails']:
                        emails.append(e['value'])
            except Exception as e:
                logger.error(f"Hunter.io error for {website_url}: {e}")
                
        # Fully Local Enrichment: If no contacts found, try finding a Contact page
        if not emails and not phones and website_url:
            try:
                # Basic attempt to find contact page
                contact_urls = [
                    website_url.rstrip('/') + '/contact',
                    website_url.rstrip('/') + '/contact-us',
                    website_url.rstrip('/') + '/fr/contact',
                    website_url.rstrip('/') + '/contactez-nous'
                ]
                for curl in contact_urls:
                    try:
                        c_resp = requests.get(curl, timeout=10)
                        if c_resp.status_code == 200:
                            logger.info(f"Checking contact page: {curl}")
                            c_soup = BeautifulSoup(c_resp.text, 'html.parser')
                            c_text = c_soup.get_text()
                            
                            c_emails = re.findall(r'[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+', c_text)
                            c_phones = re.findall(r'\b(?:\+?216[-.\s]?|00[-.\s]?216[-.\s]?)?[234579]\d(?:[-.\s]?\d{2}){3}\b|\b(?:\+?216[-.\s]?|00[-.\s]?216[-.\s]?)?[234579]\d{7}\b', c_text)
                            
                            emails.extend(c_emails)
                            phones.extend(c_phones)
                            
                            if c_emails or c_phones:
                                # Run AI on the contact page text if we found something or just to be sure
                                ai_extract = contact_extractor.extract_contact_info(c_text[:3000])
                                emails.extend(ai_extract.get('emails', []))
                                phones.extend(ai_extract.get('phones', []))
                                break # Stop checking other contact URLs
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Failed to explore contact pages for {website_url}: {e}")
                
        # Deduplicate
        emails = list(set([e.lower() for e in emails if e]))
        phones = list(set([p.replace(' ', '') for p in phones if p]))
        
        # If still no contacts, try a DuckDuckGo search
        if not emails and not phones:
            logger.info(f"No contacts found from website, falling back to DuckDuckGo search for: {company}")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                query = f"{company} Tunisie contact phone telephone email"
                ddg_url = f"https://html.duckduckgo.com/html/?q={query}"
                ddg_resp = requests.get(ddg_url, headers=headers, timeout=15)
                ddg_soup = BeautifulSoup(ddg_resp.text, 'html.parser')
                ddg_text = ddg_soup.get_text()
                
                # Broaden phone regex for Tunisisan numbers in search results
                found_phones = re.findall(r'\b(?:\+?216[-.\s]?|00[-.\s]?216[-.\s]?)?[234579]\d(?:[-.\s]?\d{2}){3}\b|\b(?:\+?216[-.\s]?|00[-.\s]?216[-.\s]?)?[234579]\d{7}\b', ddg_text)
                found_emails = re.findall(r'[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+', ddg_text)
                
                emails.extend(found_emails)
                phones.extend(found_phones)
                
                # Cleanup again
                emails = list(set([e.lower() for e in emails if e and not e.endswith('duckduckgo.com')]))
                phones = list(set([p.replace(' ', '') for p in phones if p]))
            except Exception as e:
                logger.error(f"DuckDuckGo search fallback failed for {company}: {e}")

        logger.info(f"Enrichment results for {company}: Emails: {len(emails)}, Phones: {len(phones)}")
        
        return {
            "emails": emails,
            "phones": phones
        }

web_enricher = WebEnricher()
