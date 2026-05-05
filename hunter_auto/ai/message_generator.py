from ai.ollama_client import ollama_client

class MessageGenerator:
    def generate_messages(self, name, title, company):
        prompt = f"""
        Generate a SHORT (max 3 sentences), friendly, non-salesy LinkedIn/email message in French, Arabic, and English 
        for an Ooredoo B2B sales agent reaching out to {name} who is {title} at {company}.
        Ask only for a 15-minute call or meeting. Never mention price. 
        Sign as: Ooredoo Business Team.
        
        Return ONLY JSON:
        {{
            "fr": "Bonjour...",
            "ar": "مرحبا...",
            "en": "Hello..."
        }}
        """
        
        schema = {
            "fr": "",
            "ar": "",
            "en": ""
        }
        
        result = ollama_client.generate_json(prompt, schema)
        
        return {
            "fr": result.get("fr", f"Bonjour {name}, je vous contacte au nom d'Ooredoo Business. Nous proposons des offres B2B sur-mesure pour les entreprises tunisiennes. Seriez-vous disponible pour un appel ou une réunion de 15 minutes pour vous les présenter ?"),
            "ar": result.get("ar", f"مرحباً {name}، أتواصل معك بالنيابة عن Ooredoo Business. نحن نقدم عروض B2B مصممة خصيصاً للشركات التونسية. هل يتوفر لديك 15 دقيقة لمكالمة أو اجتماع قصير؟"),
            "en": result.get("en", f"Hello {name}, I'm reaching out on behalf of Ooredoo Business. We offer tailored B2B solutions for Tunisian companies. Would you be available for a quick 15-minute call or meeting?")
        }

message_generator = MessageGenerator()
