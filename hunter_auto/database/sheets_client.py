import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEETS_ID

class SheetsClient:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        try:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
            self.client = gspread.authorize(self.creds)
            self.sheet = self.client.open_by_key(GOOGLE_SHEETS_ID)
        except Exception as e:
            print(f"Error authenticating with Google Sheets API: {e}")
            self.leads_ws = None
            self.log_ws = None
            return

        try:
            self.leads_ws = self.sheet.worksheet("Hunter_Auto_Leads")
        except Exception:
            print("Creating missing Hunter_Auto_Leads worksheet...")
            self.leads_ws = self.sheet.add_worksheet(title="Hunter_Auto_Leads", rows="1000", cols="20")
            self.leads_ws.append_row(["ID", "Company", "Name", "Title", "Phone", "Email", "LinkedIn URL", "Source", "Score", "Status", "Message Sent", "Sent At", "Notes"])

        try:
            self.log_ws = self.sheet.worksheet("Hunter_Auto_Log")
        except Exception:
            print("Creating missing Hunter_Auto_Log worksheet...")
            self.log_ws = self.sheet.add_worksheet(title="Hunter_Auto_Log", rows="1000", cols="5")
            self.log_ws.append_row(["Timestamp", "Level", "Message", "Lead ID"])

    def add_lead(self, lead_data):
        if not self.leads_ws: return
        try:
            row = [
                lead_data.get('id', ''), lead_data.get('company', ''), lead_data.get('name', ''),
                lead_data.get('title', ''), lead_data.get('phone', ''), lead_data.get('email', ''),
                lead_data.get('linkedin_url', ''), lead_data.get('source', ''), lead_data.get('score', ''),
                lead_data.get('status', 'pending'), lead_data.get('message_sent', ''),
                lead_data.get('sent_at', ''), lead_data.get('notes', '')
            ]
            self.leads_ws.append_row(row)
        except Exception as e:
            print(f"Error adding lead to Google Sheet: {e}")

    def lead_exists(self, linkedin_url=None, phone=None, company=None):
        if not self.leads_ws: return False
        try:
            if linkedin_url:
                urls = self.leads_ws.col_values(7)
                if linkedin_url in urls: return True
            if phone:
                phones = self.leads_ws.col_values(5)
                if phone in phones: return True
            if company:
                companies = self.leads_ws.col_values(2)
                if company in companies: return True
        except:
            pass
        return False

    def _safe_get_all_records(self):
        if not self.leads_ws: return []
        try:
            return self.leads_ws.get_all_records()
        except Exception:
            values = self.leads_ws.get_all_values()
            if not values or len(values) < 2: return []
            headers = [h if h else f"Col{i}" for i, h in enumerate(values[0])]
            records = []
            for row in values[1:]:
                # Pad row with empty strings if it's shorter than headers
                padded_row = row + [''] * (len(headers) - len(row))
                records.append(dict(zip(headers, padded_row)))
            return records

    def update_lead_data(self, lead_id, updates):
        if not self.leads_ws: return
        from config.logger import logger
        try:
            records = self._safe_get_all_records()
            headers = self.leads_ws.row_values(1)
            for idx, row in enumerate(records, start=2):
                if str(row.get('ID')) == str(lead_id):
                    for key, val in updates.items():
                        if key in headers:
                            col_idx = headers.index(key) + 1
                            self.leads_ws.update_cell(idx, col_idx, str(val))
                    break
        except Exception as e:
            logger.error(f"Failed to update lead data for {lead_id}: {e}")

    def get_pending_enrichment_leads(self):
        if not self.leads_ws: return []
        try:
            records = self._safe_get_all_records()
            return [r for r in records if str(r.get('Status', '')).lower() == 'pending_enrichment']
        except Exception as e:
            from config.logger import logger
            logger.error(f"Error in get_pending_enrichment_leads: {e}")
            return []

    def get_skipped_leads(self):
        if not self.leads_ws: return []
        try:
            records = self._safe_get_all_records()
            return [r for r in records if str(r.get('Status', '')).lower() == 'skipped']
        except Exception as e:
            from config.logger import logger
            logger.error(f"Error in get_skipped_leads: {e}")
            return []

    def get_pending_leads(self):
        if not self.leads_ws: return []
        try:
            records = self._safe_get_all_records()
            return [r for r in records if str(r.get('Status', '')).lower() == 'pending']
        except Exception as e:
            from config.logger import logger
            logger.error(f"Error in get_pending_leads: {e}")
            return []

    def get_all_leads(self, limit=100):
        if not self.leads_ws: return []
        try:
            records = self._safe_get_all_records()
            return records[-limit:] if records else []
        except Exception as e:
            from config.logger import logger
            logger.error(f"Error in get_all_leads: {e}")
            return []

    def update_lead_status(self, lead_id, status, notes=""):
        if not self.leads_ws: return
        try:
            records = self._safe_get_all_records()
            for idx, row in enumerate(records, start=2):
                if str(row.get('ID')) == str(lead_id):
                    self.leads_ws.update_cell(idx, 10, status)
                    if notes:
                        self.leads_ws.update_cell(idx, 13, notes)
                    break
        except:
            pass
                
    def get_stats(self):
        if not self.leads_ws: return {"total": 0, "high_score": 0, "cold_call_queue": 0, "skipped": 0}
        try:
            records = self._safe_get_all_records()
            total = len(records)
            
            high_score = 0
            for r in records:
                try:
                    if int(r.get('Score', 0) or 0) >= 7: high_score += 1
                except:
                    pass
                    
            cold_call_queue = len([r for r in records if r.get('Status') in ['cold_call_queue', 'secondary_call_queue']])
            skipped = len([r for r in records if r.get('Status') in ['skipped', 'dead']])
            return {"total": total, "high_score": high_score, "cold_call_queue": cold_call_queue, "skipped": skipped}
        except:
            return {"total": 0, "high_score": 0, "cold_call_queue": 0, "skipped": 0}

sheets_client = SheetsClient()
