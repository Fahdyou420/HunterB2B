import requests
import json
import time
from config.settings import OLLAMA_HOST, OLLAMA_MODEL
import os

class OllamaClient:
    def __init__(self):
        self.base_url = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        os.makedirs("logs", exist_ok=True)

    def generate(self, prompt, retries=3):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
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

    def generate_json(self, prompt, schema=None):
        modified_prompt = prompt + "\n\nYou MUST return a valid JSON object matching this schema or structure. No markdown blocks, just raw JSON."
        if schema:
            modified_prompt += f"\nSchema: {json.dumps(schema)}"
        
        response_text = self.generate(modified_prompt)
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[-1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[-1].split("```")[0].strip()
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from Ollama: {e}")
            return {}

    def _log_call(self, prompt, response):
        try:
            with open("logs/ollama_calls.log", "a", encoding="utf-8") as f:
                f.write(f"--- PROMPT ---\n{prompt}\n--- RESPONSE ---\n{response}\n\n")
        except:
            pass

ollama_client = OllamaClient()
