from database.sheets_client import sheets_client
from config.logger import logger

class OutreachRouter:
    def process_pending_leads(self, batch_size=50):
        logger.info("[Routing Engine] Starting Cold Call MatchMaker...")
        leads = sheets_client.get_pending_leads()
        logger.info(f"Found {len(leads)} pending leads ready for cold calling.")
        
        for lead in leads[:batch_size]:
            logger.info(f"Evaluating lead ID: {lead.get('ID')} ({lead.get('Company')})")
            lead_id = lead.get('ID')
            phone = str(lead.get('Phone', '')).strip()
            score = lead.get('Score', 0)
            try:
                score = int(score)
            except:
                score = 0
            
            try:
                if phone and score >= 7:
                    logger.info("-> Path: High Score + Phone found -> Cold Call Queue")
                    sheets_client.update_lead_status(lead_id, "cold_call_queue", "High priority for human cold calling")
                elif phone:
                    logger.info("-> Path: Low Score + Phone -> Secondary Queue")
                    sheets_client.update_lead_status(lead_id, "secondary_call_queue", "Medium priority cold calling")
                else:
                    logger.info("-> Path: No Phone -> Missing Info")
                    sheets_client.update_lead_status(lead_id, "skipped", "No phone found for cold calling")
            except Exception as e:
                logger.error(f"Error processing lead {lead_id}: {e}")

outreach_router = OutreachRouter()
