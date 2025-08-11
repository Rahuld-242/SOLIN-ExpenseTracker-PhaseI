import os
import json
from datetime import datetime

LOG_DIR = "logs"
COMMAND_LOG_FILE = os.path.join(LOG_DIR, "command_log.json")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error_log.json")

os.makedirs(LOG_DIR, exist_ok=True)

def get_log_filename(base_name):
    current_month=datetime.now().strftime("%Y-%m")
    return os.path.join(LOG_DIR, f"{base_name}_{current_month}.json")

def log_command(user_input, action=None, params=None, output=None):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "action": action,
        "params": params,
        "output": output
        }
    try:
        with open(COMMAND_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry)+"\n")
            
    except Exception as e:
        print(f"[LOGGER ERROR] Failed to write command log: {e}")
        
def log_error(user_input, action=None, params=None, error=None):
    log_entry={
         "timestamp": datetime.now().isoformat(),
         "user_input": user_input,
         "action": action,
         "params": params,
         "error": error
        }
    try:
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry)+"\n")
    except Exception as e:
        print(f"[LOGGER ERROR] Failed to write error log: {e}")