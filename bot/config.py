"""
config.py — Barcha sozlamalar .env fayldan o'qiladi
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────
BOT_TOKEN         = os.getenv("BOT_TOKEN", "")
APPROVAL_GROUP_ID = int(os.getenv("APPROVAL_GROUP_ID", "0"))
ADMIN_IDS         = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
WEBAPP_URL        = os.getenv("WEBAPP_URL", "")

# ── Supabase ──────────────────────────────────
SUPABASE_URL      = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY      = os.getenv("SUPABASE_KEY", "")

# ── To'lov ────────────────────────────────────
PAYMENT_CARD       = os.getenv("PAYMENT_CARD", "8600 0000 0000 0000")
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "")
PHONE_CONTACT      = os.getenv("PHONE_CONTACT", "+998 88 357 33 66")

# ── Maktab ────────────────────────────────────
SCHOOL_NAME = "Wunderkind Xalqaro Maktabi"

def validate():
    missing = []
    for name, val in [
        ("BOT_TOKEN", BOT_TOKEN),
        ("APPROVAL_GROUP_ID", APPROVAL_GROUP_ID),
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_KEY", SUPABASE_KEY),
    ]:
        if not val:
            missing.append(name)
    if missing:
        raise EnvironmentError(f".env da quyidagilar yo'q: {', '.join(missing)}")
