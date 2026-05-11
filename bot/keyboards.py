"""
keyboards.py — Klaviaturalar
"""
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton,
)
from bot.config import ADMIN_IDS, WEBAPP_URL


def kb_main(user_id: int) -> ReplyKeyboardMarkup:
    """Asosiy menyu — doim ko'rinadigan reply keyboard."""
    rows = [
        [KeyboardButton("📋 Mock testlar"), KeyboardButton("✍️ Ro'yxatdan o'tish")],
        [KeyboardButton("📞 Aloqa")],
    ]
    if user_id in ADMIN_IDS and WEBAPP_URL:
        rows.append([KeyboardButton("⚙️ Admin panel")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def kb_mocks(mocks: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for m in mocks:
        label = f"📌 {m['title']}  |  {m['date_str']}  |  {m['price']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"mock_info|{m['id']}")])
    rows.append([InlineKeyboardButton("🏠 Bosh menu", callback_data="back_noop")])
    return InlineKeyboardMarkup(rows)


def kb_mock_info(mock_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Shu testga ro'yxatdan o'tish", callback_data=f"reg_mock|{mock_id}")],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="mocks_list")],
    ])


def kb_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Tasdiqlash",        callback_data="confirm_yes")],
        [InlineKeyboardButton("🔄 Qaytadan boshlash", callback_data="reg_start")],
    ])


def kb_group_approval(reg_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"grp_ok|{reg_id}"),
        InlineKeyboardButton("❌ Rad etish",  callback_data=f"grp_no|{reg_id}"),
    ]])


def kb_cancel_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Bekor qilish", callback_data="back_noop")
    ]])
