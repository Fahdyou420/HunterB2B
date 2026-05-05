import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    def send_message(self, text):
        if not self.bot_token or not self.chat_id:
            return
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Telegram notification failed: {e}")

    def notify_lead(self, lead):
        msg = f"""🎯 <b>New lead ready for cold call:</b>
<b>Name:</b> {lead.get('Name', 'Unknown')}
<b>Title:</b> {lead.get('Title', 'Unknown')}
<b>Company:</b> {lead.get('Company', 'Unknown')}
<b>Phone:</b> {lead.get('Phone', 'Unknown')}
<b>Score:</b> {lead.get('Score', '-')}/10
<b>Notes:</b> {lead.get('Notes', '')}

<i>Suggested opening:</i> Bonjour {lead.get('Name', '')}, je vous contacte au nom d'Ooredoo Business..."""
        self.send_message(msg)

telegram_notifier = TelegramNotifier()
