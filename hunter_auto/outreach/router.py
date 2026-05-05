from database.sheets_client import sheets_client
from outreach.telegram_notifier import telegram_notifier
from outreach.email_sender import email_sender
from outreach.linkedin_messenger import linkedin_messenger
from config.logger import logger

class OutreachRouter:
    def process_pending_leads(self, batch_size=10):
        logger.info("[Routing Engine] Starting Contact Router...")
        leads = sheets_client.get_pending_leads()
        logger.info(f"Found {len(leads)} pending leads ready for outreach.")
        
        for lead in leads[:batch_size]:
            logger.info(f"Routing logic for lead ID: {lead.get('ID')} ({lead.get('Company')})")
            lead_id = lead.get('ID')
            phone = str(lead.get('Phone', '')).strip()
            email = str(lead.get('Email', '')).strip()
            li_url = str(lead.get('LinkedIn URL', '')).strip()
            
            try:
                if phone:
                    logger.info("-> Path: Phone found -> Human Handoff (Telegram)")
                    telegram_notifier.notify_lead(lead)
                    sheets_client.update_lead_status(lead_id, "phone_handoff")
                elif email:
                    logger.info("-> Path: Email found -> Automated Email Sequence")
                    success = email_sender.send_email(lead)
                    if success:
                        if li_url:
                            logger.info("   -> Bonus: LinkedIn URL found -> Automated LI Message")
                            linkedin_messenger.send_message(lead)
                        sheets_client.update_lead_status(lead_id, "email_sent")
                elif li_url:
                    logger.info("-> Path: LinkedIn Only -> Automated LI Sequence")
                    success = linkedin_messenger.send_message(lead)
                    if success:
                        sheets_client.update_lead_status(lead_id, "linkedin_sent")
                else:
                    logger.info("-> Path: Dead End -> Skipped")
                    sheets_client.update_lead_status(lead_id, "skipped", "No contact info found")
            except Exception as e:
                logger.error(f"Error processing lead {lead_id}: {e}")

outreach_router = OutreachRouter()
