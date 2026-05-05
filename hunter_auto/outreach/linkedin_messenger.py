import time
import random
from ai.message_generator import message_generator

class LinkedinMessenger:
    def send_message(self, lead):
        url = lead.get('LinkedIn URL')
        if not url: return False
        
        name = lead.get('Name', '')
        title = lead.get('Title', '')
        company = lead.get('Company', '')
        
        msgs = message_generator.generate_messages(name, title, company)
        content_fr = msgs['fr']
        
        print(f"Would send LinkedIn message to {url}:\n{content_fr[:50]}...")
        
        # Real logic would use playwright with stored session to visit profile
        # Check if connected -> .message-anywhere-button
        # If not -> connection request with note
        
        time.sleep(random.uniform(2, 5))
        return True

linkedin_messenger = LinkedinMessenger()
