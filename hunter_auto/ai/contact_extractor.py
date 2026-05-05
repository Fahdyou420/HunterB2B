from ai.ollama_client import ollama_client

class ContactExtractor:
    def extract_contact_info(self, raw_text):
        prompt = f"""
        Extract structured contact information from the following raw text. Find any names, emails, and phone numbers.
        Text:
        {raw_text}
        
        Return ONLY a JSON object with keys "emails", "phones", and "names" as lists of strings. 
        Focus especially on Tunisian phone formats (+216, 00216, or local 8-digit numbers).
        Do not output any markdown formatting like ```json.
        """
        
        schema = {
            "emails": [],
            "phones": [],
            "names": []
        }
        
        result = ollama_client.generate_json(prompt, schema)
        return result

contact_extractor = ContactExtractor()
