"""
handlers/group.py — Guruhda tasdiqlash / rad etish
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot import database as db
from bot.config import PHONE_CONTACT


async def group_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parts = query.data.split("|")
    if len(parts) != 2:
        await query.answer("❌ Noto'g'ri so'rov", show_alert=True)
        return

    action, reg_id = parts
    actor = query.from_user

    reg = await db.get_registration(reg_id)
    if not reg:
        await query.answer("❌ Ro'yxat topilmadi!", show_alert=True)
        return

    if reg["status"] != "pending":
        label = "✅ Tasdiqlangan" if reg["status"] == "approved" else "❌ Rad etilgan"
        await query.answer(f"Bu ariza allaqachon ko'rib chiqilgan: {label}", show_alert=True)
        return

    actor_name = f"@{actor.username}" if actor.username else actor.first_name

    if action == "grp_ok":
        await db.update_registration_status(reg_id, "approved", actor_name)
        user_msg = (
            "✅ *To'lovingiz tasdiqlandi!*\n\n"
            f"🆔 Raqam: `{reg_id}`\n"
            f"📌 Test: {reg['mock_title']}\n"
            f"🗓 Sana: {reg['mock_date']}\n\n"
            "📍 Manzil: Wunderkind Xalqaro Maktabi\n"
            f"📞 Savollar: {PHONE_CONTACT}\n\n"
            "Omad tilaymiz! 🍀"
        )
        group_note = f"\n\n✅ *Tasdiqladi:* {actor_name}"
        await query.answer("✅ Tasdiqlandi!")
    else:
        await db.update_registration_status(reg_id, "rejected", actor_name)
        user_msg = (
            "❌ *To'lovingiz tasdiqlanmadi.*\n\n"
            "Sabab: to'lov topilmadi yoki summa noto'g'ri.\n\n"
            "Nima qilish kerak:\n"
            "1️⃣ To'lovni qaytadan amalga oshiring\n"
            "2️⃣ /start dan ro'yxatdan o'ting\n\n"
            f"📞 Yordam: {PHONE_CONTACT}"
        )
        group_note = f"\n\n❌ *Rad etdi:* {actor_name}"
        await query.answer("❌ Rad etildi!")

    try:
        await context.bot.send_message(
            chat_id=reg["user_tg_id"],
            text=user_msg,
            parse_mode="Markdown",
        )
    except Exception:
        pass

    try:
        old_caption = query.message.caption or ""
        await query.edit_message_caption(
            caption=old_caption + group_note,
            parse_mode="Markdown",
            reply_markup=None,
        )
    except Exception:
        pass


def build_group_handlers() -> list:
    return [
        CallbackQueryHandler(group_action, pattern=r"^grp_(ok|no)\|.+$"),
    ]
