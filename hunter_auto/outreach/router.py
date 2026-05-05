from database.sheets_client import sheets_client
from outreach.telegram_notifier import telegram_notifier
from outreach.email_sender import email_sender
from outreach.linkedin_messenger import linkedin_messenger

class OutreachRouter:
    def process_pending_leads(self, batch_size=10):
        leads = sheets_client.get_pending_leads()
        print(f"Found {len(leads)} pending leads to process.")
        
        for lead in leads[:batch_size]:
            print(f"Processing lead ID: {lead.get('ID')}")
            lead_id = lead.get('ID')
            phone = str(lead.get('Phone', '')).strip()
            email = str(lead.get('Email', '')).strip()
            li_url = str(lead.get('LinkedIn URL', '')).strip()
            
            try:
                if phone:
                    print("Found phone, sending to telegram.")
                    telegram_notifier.notify_lead(lead)
                    sheets_client.update_lead_status(lead_id, "phone_handoff")
                elif email:
                    print("Found email, sending email.")
                    success = email_sender.send_email(lead)
                    if success:
                        if li_url:
                            linkedin_messenger.send_message(lead)
                        sheets_client.update_lead_status(lead_id, "email_sent")
                elif li_url:
                    print("Only LinkedIn URL, sending LI message.")
                    success = linkedin_messenger.send_message(lead)
                    if success:
                        sheets_client.update_lead_status(lead_id, "linkedin_sent")
                else:
                    sheets_client.update_lead_status(lead_id, "skipped", "No contact info found")
            except Exception as e:
                print(f"Error processing lead {lead_id}: {e}")

outreach_router = OutreachRouter()
