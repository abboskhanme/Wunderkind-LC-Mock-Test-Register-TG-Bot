"""
utils.py — Yordamchi funksiyalar
"""
import logging
from bot.config import ADMIN_IDS

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def fmt_mock(mock: dict) -> str:
    desc = f"\n📝 {mock['description']}" if mock.get("description") else ""
    return (
        f"📌 *{mock['title']}*\n"
        f"🗓 Sana: {mock['date_str']}\n"
        f"📍 Manzil: {mock['location']}\n"
        f"💰 Narx: {mock['price']}"
        f"{desc}"
    )


def fmt_reg_summary(d: dict) -> str:
    return (
        f"👤 Ism: *{d['full_name']}*\n"
        f"📱 Telefon: {d['phone']}\n"
        f"📌 Test: {d['mock_title']}\n"
        f"🗓 Sana: {d['mock_date']}\n"
        f"💰 Narx: {d['price']}"
    )


def fmt_group_msg(reg: dict, username: str) -> str:
    uname = f"@{username}" if username else "yo'q"
    return (
        f"🔔 *Yangi ariza*\n\n"
        f"🆔 `{reg['id']}`\n"
        f"👤 {reg['full_name']}\n"
        f"📱 {reg['phone']}\n"
        f"💬 Telegram: {uname}\n"
        f"📌 {reg['mock_title']}\n"
        f"🗓 {reg['mock_date']}\n"
        f"💰 {reg['price']}"
    )


def validate_phone(text: str) -> str | None:
    """
    +998XXXXXXXXX yoki 998XXXXXXXXX → +998XXXXXXXXX
    Noto'g'ri bo'lsa None qaytaradi.
    """
    cleaned = text.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("998") and len(cleaned) == 12 and cleaned.isdigit():
        cleaned = "+" + cleaned
    if cleaned.startswith("+998") and len(cleaned) == 13 and cleaned[1:].isdigit():
        return cleaned
    return None


async def safe_edit(query, text: str, parse_mode: str = "Markdown", **kwargs):
    """Xavfsiz edit_message_text."""
    try:
        await query.edit_message_text(text, parse_mode=parse_mode, **kwargs)
    except Exception:
        try:
            await query.message.reply_text(text, parse_mode=parse_mode, **kwargs)
        except Exception as e:
            logger.warning(f"safe_edit xatolik: {e}")
