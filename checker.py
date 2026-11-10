import datetime
import json
import os
import time
import hmac
import hashlib
from zoneinfo import ZoneInfo
import requests

# Ключи из секретов GitHub
CLIENT_ID = os.environ.get("TUYA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TUYA_CLIENT_SECRET")
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Базовый URL для региона Европа
BASE_URL = "https://openapi.tuyaeu.com"

def send_telegram_notification(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")

def get_tuya_token():
    try:
        t = str(int(time.time() * 1000))
        # Подпись для получения токена: HMAC-SHA256(client_id + t, secret)
        message = CLIENT_ID + t
        sign = hmac.new(
            CLIENT_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

        url = f"{BASE_URL}/v1.0/token?grant_type=1"
        headers = {
            "client_id": CLIENT_ID,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get("success"):
            return data["result"]["access_token"]
        else:
            print(f"Tuya Token Error: {data}")
            return None
    except Exception as e:
        print(f"Exception during token request: {e}")
        return None

def get_device_status(access_token):
    try:
        t = str(int(time.time() * 1000))
        # Подпись для запросов с токеном: HMAC-SHA256(client_id + access_token + t, secret)
        message = CLIENT_ID + access_token + t
        sign = hmac.new(
            CLIENT_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

        url = f"{BASE_URL}/v1.0/devices/{DEVICE_ID}"
        headers = {
            "client_id": CLIENT_ID,
            "access_token": access_token,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if data.get("success"):
            # Поле 'online' возвращает True, если розетка на связи с облаком (есть свет и интернет)
            is_online = data["result"].get("online", False)
            return "online" if is_online else "offline"
        else:
            print(f"Tuya Device Status Error: {data}")
            return None
    except Exception as e:
        print(f"Exception during device status request: {e}")
        return None

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

    last_status = logs[-1]["status"] if logs else "online"

    # Получаем токен доступа Tuya
    token = get_tuya_token()
    if not token:
        print("Could not obtain Tuya token, skipping this check.")
        return

    # Запрашиваем реальный статус розетки
    current_status = get_device_status(token)
    if not current_status:
        print("Could not get device status, skipping.")
        return

    now_time = datetime.datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M:%S")

    # Уведомление отправляется ТОЛЬКО при смене статуса
    if last_status != current_status:
        if current_status == "offline":
            send_telegram_notification(f"⚠️ <b>Увага! Світло зникло!</b>\nЧас: {now_time}")
        elif current_status == "online":
            send_telegram_notification(f"🟢 <b>Світло з'явилося!</b>\nЧас: {now_time}")

    # Записываем актуальный статус в историю
    logs.append({"time": now_time, "status": current_status})
    logs = logs[-50:]

    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

if __name__ == "__main__":
    update_logs()
