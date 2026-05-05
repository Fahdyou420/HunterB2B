from database.sheets_client import sheets_client
from scrapers.web_enricher import web_enricher
from ai.lead_scorer import lead_scorer
from config.logger import logger

class EnrichmentEngine:
    def process_pending_enrichment(self):
        logger.info("[Layer 2] Starting AI Enrichment & Scoring Engine...")
        leads = sheets_client.get_pending_enrichment_leads()
        
        if not leads:
            logger.info("No leads pending enrichment.")
            return

        for lead in leads:
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
            if not email or not phone:
                if website:
                    enrich_res = web_enricher.enrich_lead(company, website)
                    if enrich_res.get('emails') and not email:
                        email = enrich_res['emails'][0]
                    if enrich_res.get('phones') and not phone:
                        phone = enrich_res['phones'][0]
            
            # 2. AI Scoring
            logger.info(f"Scoring lead via Ollama: {company}")
            score, reason = lead_scorer.score_lead({"company": company, "title": lead.get('Title', '')})
            
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
