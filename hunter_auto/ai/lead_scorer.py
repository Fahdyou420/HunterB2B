from ai.ollama_client import ollama_client

class LeadScorer:
    def score_lead(self, lead_data):
        prompt = f"""
        Rate this Tunisian company's likelihood of needing B2B telecom packages (phone lines, internet, mobile fleet).
        Company: {lead_data.get('company', 'Unknown')}
        Title of Contact: {lead_data.get('title', 'Unknown')}
        Sector: {lead_data.get('sector', 'Unknown')}
        
        High score = large company, many employees, no obvious existing telecom contract signals.
        Return ONLY a JSON: {{"score": 5, "reason": "..."}}
        """
        
        schema = {
            "score": 0,
            "reason": ""
        }
        
        result = ollama_client.generate_json(prompt, schema)
        score = result.get('score', 5)
        reason = result.get('reason', 'No specific reason provided.')
        
        return score, reason

lead_scorer = LeadScorer()
