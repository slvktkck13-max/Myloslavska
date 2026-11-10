import datetime
import json
import os
import time
import requests

# Ключи берутся из секретов GitHub
CLIENT_ID = os.environ.get("TUYA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TUYA_CLIENT_SECRET")
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID")

# Базовый URL для регионов Европа (Tuya Cloud)
BASE_URL = "https://openapi.tuyaeu.com"

def get_tuya_token():
    try:
        t = str(int(time.time() * 1000))
        url = f"{BASE_URL}/v1.0/token?grant_type=1"
        headers = {
            "client_id": CLIENT_ID,
            "sign": "1",
            "t": t,
            "sign_method": "HMAC-SHA256"
        }
        return True
    except Exception as e:
        return False

def update_logs():
    filename = "logs.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    else:
        logs = []

    current_status = "online" 
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs.append({"time": now_time, "status": current_status})

    # Сохраняем только последние 50 записей, чтобы файл не разрастался
    logs = logs[-50:]

    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

if __name__ == "__main__":
    update_logs()
