"""
handlers/admin.py — Admin uchun bot buyruqlari
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, filters
from bot import database as db
from bot.utils import is_admin
from bot.config import WEBAPP_URL, ADMIN_IDS


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Ruxsat yo'q.")
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


@admin_only
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = await db.get_stats()
    await update.message.reply_text(
        "📊 *Statistika:*\n\n"
        f"📋 Jami arizalar: *{stats.get('total', 0)}*\n"
        f"✅ Tasdiqlangan: *{stats.get('approved', 0)}*\n"
        f"⏳ Kutilmoqda: *{stats.get('pending', 0)}*\n"
        f"❌ Rad etilgan: *{stats.get('rejected', 0)}*\n"
        f"📌 Faol testlar: *{stats.get('active_mocks', 0)}*",
        parse_mode="Markdown",
    )


@admin_only
async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if WEBAPP_URL:
        await update.message.reply_text(
            "⚙️ Admin panelni oching:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🖥 Admin panel", web_app={"url": WEBAPP_URL})
            ]])
        )
    else:
        await update.message.reply_text("⚠️ WEBAPP_URL sozlanmagan.")


def build_admin_handlers() -> list:
    return [
        CommandHandler("stats", cmd_stats, filters=filters.User(user_id=ADMIN_IDS)),
        CommandHandler("panel", cmd_panel, filters=filters.User(user_id=ADMIN_IDS)),
    ]
