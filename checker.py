import datetime
import json
import os
import time
import hmac
import hashlib
from zoneinfo import ZoneInfo
import requests

CLIENT_ID = os.environ.get("TUYA_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("TUYA_CLIENT_SECRET", "").strip()
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID", "").strip()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

BASE_URL = "https://openapi.tuyaeu.com"

def get_tuya_token():
    try:
        t = str(int(time.time() * 1000))
        # Для получения токена строка сообщения: client_id + t
        message = CLIENT_ID + t
        sign = hmac.new(
            CLIENT_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

        # Выводим отладочную информацию в логи Actions (секрет не показываем целиком в целях безопасности)
        print(f"DEBUG: CLIENT_ID length = {len(CLIENT_ID)}, CLIENT_SECRET length = {len(CLIENT_SECRET)}")
        print(f"DEBUG: Sign Message = '{message}'")
        print(f"DEBUG: Generated Sign = '{sign}'")

        url = f"{BASE_URL}/v1.0/token?grant_type=1"
        headers = {
            "client_id": CLIENT_ID,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        print("Tuya Token Response:", data)
        
        if data.get("success"):
            return data["result"]["access_token"]
        else:
            print(f"Tuya Token Error: {data}")
            return None
    except Exception as e:
        print(f"Exception during token request: {e}")
        return None

def update_logs():
    token = get_tuya_token()
    if not token:
        print("Could not obtain Tuya token")
        return
    print("Success! Token obtained.")

if __name__ == "__main__":
    update_logs()
