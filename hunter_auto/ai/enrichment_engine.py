from database.sheets_client import sheets_client
from scrapers.web_enricher import web_enricher
from ai.lead_scorer import lead_scorer
from config.logger import logger

class EnrichmentEngine:
    def process_pending_enrichment(self):
        logger.info("[Layer 2] Starting AI Enrichment & Scoring Engine...")
        leads = sheets_client.get_pending_enrichment_leads()
        skipped_leads = sheets_client.get_skipped_leads()
        
        # combine lists but limit skipped leads to avoid huge loops on old leads
        all_leads = leads + skipped_leads[:20]
        
        if not all_leads:
            logger.info("No leads pending enrichment.")
            return

        for lead in all_leads:
            lead_id = lead.get('ID')
            company = lead.get('Company', 'Unknown')
            notes = str(lead.get('Notes', ''))
            
            website = ""
            if "WEBSITE:" in notes:
                website = notes.split("WEBSITE:")[1].strip()
                
            email = str(lead.get('Email', ''))
            phone = str(lead.get('Phone', ''))
            
            logger.info(f"Enriching lead: {company}")
            
            # 1. Extract contacts if missing
            if not email and not phone:
                enrich_res = web_enricher.enrich_lead(company, website)
                if enrich_res.get('emails') and not email:
                    email = enrich_res['emails'][0]
                if enrich_res.get('phones') and not phone:
                    phone = enrich_res['phones'][0]

            if lead.get('Status') == 'skipped' and not phone:
                logger.info(f"Still no phone found for {company} after deep search. Marking as dead.")
                sheets_client.update_lead_status(lead_id, "dead", "No phone found after deep search")
                continue

            # 1.5 Gather Company Intelligence via DuckDuckGo before Scoring
            company_intel = ""
            try:
                import requests
                from bs4 import BeautifulSoup
                intel_headers = {'User-Agent': 'Mozilla/5.0'}
                intel_query = f"{company} Tunisie à propos entreprise"
                intel_url = f"https://html.duckduckgo.com/html/?q={intel_query}"
                intel_resp = requests.get(intel_url, headers=intel_headers, timeout=10)
                intel_soup = BeautifulSoup(intel_resp.text, 'html.parser')
                snippets = [a.get_text() for a in intel_soup.find_all('a', class_='result__snippet')]
                company_intel = " | ".join(snippets[:3])
            except Exception as e:
                logger.error(f"Failed to gather company intel for {company}: {e}")

            # 2. AI Scoring
            logger.info(f"Scoring lead via Ollama: {company}")
            score, reason = lead_scorer.score_lead({
                "company": company, 
                "title": lead.get('Title', ''),
                "intel": company_intel
            })
            
            logger.info(f"AI Score for {company}: {score}/10")
            
            # 3. Update Sheet
            updates = {
                "Score": score,
                "Status": "pending",  # Move to outreach pool
                "Notes": f"AI Reason: {reason} | Original Notes: {notes}"
            }
            if email: updates["Email"] = email
            if phone: updates["Phone"] = phone
            
            sheets_client.update_lead_data(lead_id, updates)
            logger.info(f"Lead {company} successfully enriched and ready for routing.")

enrichment_engine = EnrichmentEngine()
