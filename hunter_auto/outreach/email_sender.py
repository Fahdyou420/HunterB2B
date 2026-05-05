import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from ai.message_generator import message_generator

class EmailSender:
    def send_email(self, lead):
        to_email = lead.get('Email')
        if not to_email or not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
            return False
            
        name = lead.get('Name', 'Bonjour')
        title = lead.get('Title', '')
        company = lead.get('Company', 'votre entreprise')
        
        msgs = message_generator.generate_messages(name, title, company)
        content_fr = msgs['fr']
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Proposition Ooredoo Business pour {company}"
        msg["From"] = f"Ooredoo Business Team <{GMAIL_ADDRESS}>"
        msg["To"] = to_email

        content_fr_html = content_fr.replace('\n', '<br>')
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <p>{content_fr_html}</p>
            <br>
            <p style="color: #E30613; font-weight: bold;">Équipe Ooredoo Business</p>
          </body>
        </html>
        """
        
        part2 = MIMEText(html, "html")
        msg.attach(part2)

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

email_sender = EmailSender()
