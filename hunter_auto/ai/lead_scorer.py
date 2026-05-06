from ai.ollama_client import ollama_client

class LeadScorer:
    def score_lead(self, lead_data):
        prompt = f"""
        You are an elite B2B sales intelligence agent. 
        Rate this prospect's likelihood of being a high-value B2B client based on their profile.
        
        Company: {lead_data.get('company', 'Unknown')}
        Title of Contact: {lead_data.get('title', 'Unknown')}
        Sector: {lead_data.get('sector', 'Unknown')}
        Recent Web Intel: {lead_data.get('intel', 'No specific web data found.')}
        
        A high score (8-10) means: They are clearly a decision maker (CEO, Founder, Director) in a fast-growing, highly-invested sector, or the web intel shows they are a large established business.
        A medium score (4-7) means: Operational role or generic business.
        A low score (1-3) means: Low buying power or irrelevant target.
        
        Analyze the intelligence. Return ONLY a JSON object: {{"score": 5, "reason": "short explanation of buying power/fit"}}
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
