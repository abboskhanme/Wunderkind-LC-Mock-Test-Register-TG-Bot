"""
main.py — Ishga tushirish nuqtasi
"""
import asyncio
import logging
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bot.config import BOT_TOKEN, validate
from bot.handlers.user import (
    cmd_start, build_user_conv,
    handle_menu_button,
    show_mocks, show_mock_info, show_contact,
)
from bot.handlers.group import build_group_handlers
from bot.handlers.admin import build_admin_handlers

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.WARNING,
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def main():
    validate()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(build_user_conv())

    for h in build_group_handlers():
        app.add_handler(h)

    for h in build_admin_handlers():
        app.add_handler(h)

    # Inline callback handlerlar
    app.add_handler(CallbackQueryHandler(show_mocks,     pattern=r"^mocks_list$"))
    app.add_handler(CallbackQueryHandler(show_mock_info, pattern=r"^mock_info\|.+$"))
    app.add_handler(CallbackQueryHandler(show_contact,   pattern=r"^contact$"))

    # Reply keyboard tugmalarini ushlash
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"^(📋 Mock testlar|✍️ Ro'yxatdan o'tish|📞 Aloqa|⚙️ Admin panel)$"),
        handle_menu_button,
    ))

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
        )
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
