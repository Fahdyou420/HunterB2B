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
            self.leads_ws = self.sheet.worksheet("Hunter_Auto_Leads")
            self.log_ws = self.sheet.worksheet("Hunter_Auto_Log")
        except Exception as e:
            print(f"Error authenticating with Google Sheets: {e}")
            self.leads_ws = None
            self.log_ws = None

    def add_lead(self, lead_data):
        if not self.leads_ws: return
        row = [
            lead_data.get('id', ''), lead_data.get('company', ''), lead_data.get('name', ''),
            lead_data.get('title', ''), lead_data.get('phone', ''), lead_data.get('email', ''),
            lead_data.get('linkedin_url', ''), lead_data.get('source', ''), lead_data.get('score', ''),
            lead_data.get('status', 'pending'), lead_data.get('message_sent', ''),
            lead_data.get('sent_at', ''), lead_data.get('notes', '')
        ]
        self.leads_ws.append_row(row)

    def lead_exists(self, linkedin_url=None, phone=None):
        if not self.leads_ws: return False
        try:
            if linkedin_url:
                urls = self.leads_ws.col_values(7)
                if linkedin_url in urls: return True
            if phone:
                phones = self.leads_ws.col_values(5)
                if phone in phones: return True
        except:
            pass
        return False

    def get_pending_leads(self):
        if not self.leads_ws: return []
        try:
            records = self.leads_ws.get_all_records()
            return [r for r in records if str(r.get('Status', '')).lower() == 'pending']
        except:
            return []

    def get_all_leads(self, limit=100):
        if not self.leads_ws: return []
        try:
            records = self.leads_ws.get_all_records()
            return records[-limit:]  # return the newest subset
        except:
            return []

    def update_lead_status(self, lead_id, status, notes=""):
        if not self.leads_ws: return
        try:
            records = self.leads_ws.get_all_records()
            for idx, row in enumerate(records, start=2):
                if str(row.get('ID')) == str(lead_id):
                    self.leads_ws.update_cell(idx, 10, status)
                    if notes:
                        self.leads_ws.update_cell(idx, 13, notes)
                    break
        except:
            pass
                
    def get_stats(self):
        if not self.leads_ws: return {"total": 0, "sent": 0, "meetings": 0, "response_rate": "0%"}
        try:
            records = self.leads_ws.get_all_records()
            total = len(records)
            sent = len([r for r in records if r.get('Status') in ['linkedin_sent', 'email_sent', 'responded', 'meeting_booked']])
            meetings = len([r for r in records if r.get('Status') == 'meeting_booked'])
            response_rate = f"{(len([r for r in records if r.get('Status') in ['responded', 'meeting_booked']]) / sent * 100):.1f}%" if sent > 0 else "0%"
            return {"total": total, "sent": sent, "meetings": meetings, "response_rate": response_rate}
        except:
            return {"total": 0, "sent": 0, "meetings": 0, "response_rate": "0%"}

sheets_client = SheetsClient()
