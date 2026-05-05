import requests
import json
import time
import config.settings as app_settings
import os

class OllamaClient:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)

    def generate(self, prompt, retries=3):
        url = f"{app_settings.OLLAMA_HOST}/api/generate"
        payload = {
            "model": app_settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json().get('response', '').strip()
                self._log_call(prompt, result)
                return result
            except Exception as e:
                print(f"Ollama connection error (attempt {attempt+1}): {e}")
                time.sleep(2)
        return ""

    def generate_json(self, prompt, schema=None, default_return=None):
        modified_prompt = prompt + "\n\nYou MUST return a valid JSON object matching this schema or structure. No markdown blocks, just raw JSON."
        if schema:
            modified_prompt += f"\nSchema: {json.dumps(schema)}"
        
        response_text = self.generate(modified_prompt)
        try:
            # Clean up the response to isolate the JSON
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
                
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
                
            # Fallback if there's text before/after the backticks
            if "```json" in response_text:
                cleaned = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in response_text:
                cleaned = response_text.split("```", 1)[1].split("```", 1)[0].strip()
                
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            from config.logger import logger
            logger.error(f"Failed to parse JSON from Ollama: {e}\nRaw output: {response_text}")
            return default_return if default_return is not None else {}

    def _log_call(self, prompt, response):
        try:
            with open("logs/ollama_calls.log", "a", encoding="utf-8") as f:
                f.write(f"--- PROMPT ---\n{prompt}\n--- RESPONSE ---\n{response}\n\n")
        except:
            pass

ollama_client = OllamaClient()
