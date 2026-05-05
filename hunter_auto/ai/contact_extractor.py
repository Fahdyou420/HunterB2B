from ai.ollama_client import ollama_client

class ContactExtractor:
    def extract_contact_info(self, raw_text):
        prompt = f"""
        Extract structured contact information from the following raw text. Find any names, emails, and phone numbers.
        Text:
        {raw_text}
        
        Return a JSON with lists of emails, phone numbers (especially Tunisian format starting with +216 or 00216), and names.
        """
        
        schema = {
            "emails": [],
            "phones": [],
            "names": []
        }
        
        result = ollama_client.generate_json(prompt, schema)
        return result

contact_extractor = ContactExtractor()
