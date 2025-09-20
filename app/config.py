"""
config.py
Lê variáveis de ambiente e centraliza configurações do app.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
JWT_ACCESS_EXPIRE_MIN = int(os.getenv("JWT_ACCESS_EXPIRE_MIN", "15"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
INIT_ADMIN_SECRET = os.getenv("INIT_ADMIN_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
THINGSPEAK_API_KEYS = json.loads(os.getenv("THINGSPEAK_API_KEYS", "{}"))
THINGSPEAK_CHANNELS = json.loads(os.getenv("THINGSPEAK_CHANNELS", "{}"))
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT") or 0)
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
