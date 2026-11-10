import datetime
import json
import os
import time
from zoneinfo import ZoneInfo
import requests

CLIENT_ID = os.environ.get("TUYA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TUYA_CLIENT_SECRET")
DEVICE_ID = os.environ.get("TUYA_DEVICE_ID")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

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

    # 1. Получаем предыдущий статус из последней записи в файле
    last_status = logs[-1]["status"] if logs else "online"

    # 2. Актуальный статус розетки (пока заглушка "online")
    current_status = "online" 

    now_time = datetime.datetime.now(ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M:%S")

    # 3. УВЕДОМЛЕНИЕ ОТПРАВЛЯЕТСЯ ТОЛЬКО ПРИ ИЗМЕНЕНИИ СТАТУСА
    if last_status != current_status:
        if current_status == "offline":
            send_telegram_notification(f"⚠️ <b>Увага! Світло зникло!</b>\nЧас: {now_time}")
        elif current_status == "online":
            send_telegram_notification(f"🟢 <b>Світло з'явилося!</b>\nЧас: {now_time}")

    # Записываем свежий статус в историю
    logs.append({"time": now_time, "status": current_status})
    logs = logs[-50:]

    with open(filename, "w") as f:
        json.dump(logs, f, indent=2)

if __name__ == "__main__":
    update_logs()
