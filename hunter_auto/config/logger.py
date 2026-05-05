import logging
import os

os.makedirs("logs", exist_ok=True)
log_file = "logs/app.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("HunterAuto")

def get_recent_logs(lines=50):
    try:
        if not os.path.exists(log_file):
            return "System initialized. Waiting for events...\n"
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except Exception as e:
        return f"Could not read logs: {e}"
