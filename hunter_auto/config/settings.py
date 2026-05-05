import os
from dotenv import load_dotenv, set_key

load_dotenv()

ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "./config/credentials.json")

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

HUNTER_IO_API_KEY = os.getenv("HUNTER_IO_API_KEY")

TARGET_SECTORS = [s.strip() for s in os.getenv("TARGET_SECTORS", "Banque,Industrie,Commerce,IT").split(",")]
OUTREACH_DAILY_LIMIT = int(os.getenv("OUTREACH_DAILY_LIMIT", "15"))
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "2"))
TIMEZONE = os.getenv("TIMEZONE", "Africa/Tunis")

def update_settings(new_settings):
    global OLLAMA_HOST, OLLAMA_MODEL, TARGET_SECTORS, OUTREACH_DAILY_LIMIT, SCRAPE_INTERVAL_HOURS, TIMEZONE
    
    if "OLLAMA_HOST" in new_settings:
        OLLAMA_HOST = new_settings["OLLAMA_HOST"]
        set_key(ENV_PATH, "OLLAMA_HOST", OLLAMA_HOST)
    if "OLLAMA_MODEL" in new_settings:
        OLLAMA_MODEL = new_settings["OLLAMA_MODEL"]
        set_key(ENV_PATH, "OLLAMA_MODEL", OLLAMA_MODEL)
    if "TARGET_SECTORS" in new_settings:
        TARGET_SECTORS = new_settings["TARGET_SECTORS"]
        set_key(ENV_PATH, "TARGET_SECTORS", ",".join(TARGET_SECTORS))
    if "OUTREACH_DAILY_LIMIT" in new_settings:
        OUTREACH_DAILY_LIMIT = int(new_settings["OUTREACH_DAILY_LIMIT"])
        set_key(ENV_PATH, "OUTREACH_DAILY_LIMIT", str(OUTREACH_DAILY_LIMIT))
    if "SCRAPE_INTERVAL_HOURS" in new_settings:
        SCRAPE_INTERVAL_HOURS = int(new_settings["SCRAPE_INTERVAL_HOURS"])
        set_key(ENV_PATH, "SCRAPE_INTERVAL_HOURS", str(SCRAPE_INTERVAL_HOURS))
    if "TIMEZONE" in new_settings:
        TIMEZONE = new_settings["TIMEZONE"]
        set_key(ENV_PATH, "TIMEZONE", TIMEZONE)
