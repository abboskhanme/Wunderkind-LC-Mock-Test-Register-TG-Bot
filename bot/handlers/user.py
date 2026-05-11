"""
handlers/user.py — Foydalanuvchi ro'yxat jarayoni
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)
from bot import database as db
from bot.keyboards import (
    kb_main, kb_mocks, kb_mock_info,
    kb_confirm, kb_cancel_inline, kb_group_approval,
)
from bot.utils import fmt_mock, fmt_reg_summary, fmt_group_msg, validate_phone
from bot.config import (
    PAYMENT_CARD, PAYMENT_CARD_OWNER,
    APPROVAL_GROUP_ID, SCHOOL_NAME, PHONE_CONTACT,
    WEBAPP_URL, ADMIN_IDS,
)

GET_NAME, GET_PHONE, GET_RECEIPT, CONFIRM = range(4)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    text = (
        f"👋 Salom, *{user.first_name}*!\n\n"
        f"🏫 *{SCHOOL_NAME}*\n\n"
        "Bu bot orqali mock testlarga ro'yxatdan o'tishingiz mumkin.\n\n"
        "👇 Tugmani tanlang:"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text, parse_mode="Markdown", reply_markup=kb_main(user.id)
        )
    else:
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=kb_main(user.id)
        )
    return ConversationHandler.END


async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    if text == "📋 Mock testlar":
        await _show_mocks_msg(update, context)
    elif text == "✍️ Ro'yxatdan o'tish":
        await _reg_start_msg(update, context)
    elif text == "📞 Aloqa":
        await _show_contact_msg(update, context)
    elif text == "⚙️ Admin panel" and user.id in ADMIN_IDS and WEBAPP_URL:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        await update.message.reply_text(
            "⚙️ Admin panelni oching:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🖥 Admin panel", web_app={"url": WEBAPP_URL})
            ]])
        )


async def _show_mocks_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mocks = await db.get_active_mocks()
    if not mocks:
        await update.message.reply_text(
            "📭 Hozircha rejalashtirilgan mock test yo'q.\n\nTez orada e'lon qilinadi! 🔔",
            reply_markup=kb_main(update.effective_user.id),
        )
        return
    await update.message.reply_text(
        "📅 *Kelgusi mock testlar:*\n\nQuyidagidan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=kb_mocks(mocks),
    )


async def show_mocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mocks = await db.get_active_mocks()
    if not mocks:
        await query.message.reply_text("📭 Hozircha rejalashtirilgan mock test yo'q.\n\nTez orada e'lon qilinadi! 🔔")
        return
    await query.message.reply_text(
        "📅 *Kelgusi mock testlar:*\n\nQuyidagidan birini tanlang 👇",
        parse_mode="Markdown",
        reply_markup=kb_mocks(mocks),
    )


async def show_mock_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mock_id = query.data.split("|")[1]
    mock = await db.get_mock_by_id(mock_id)
    if not mock:
        await query.message.reply_text("❌ Test topilmadi.")
        return
    text = fmt_mock(mock) + "\n\nQatnashmoqchimisiz? 👇"
    photo = mock.get("photo_url") or mock.get("photo_id")
    if photo:
        try:
            await query.message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode="Markdown",
                reply_markup=kb_mock_info(mock_id),
            )
            return
        except Exception:
            pass
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb_mock_info(mock_id))


async def reg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if "|" in query.data:
        mock_id = query.data.split("|")[1]
        mock = await db.get_mock_by_id(mock_id)
        if mock:
            context.user_data["mock"] = mock
    if "mock" not in context.user_data:
        mocks = await db.get_active_mocks()
        if not mocks:
            await query.message.reply_text("📭 Hozircha ro'yxatdan o'tish uchun test yo'q.")
            return ConversationHandler.END
        if len(mocks) == 1:
            context.user_data["mock"] = mocks[0]
        else:
            await query.message.reply_text("📋 Qaysi testga ro'yxatdan o'tmoqchisiz?", reply_markup=kb_mocks(mocks))
            return ConversationHandler.END
    await query.message.reply_text(
        "✍️ *1-qadam: Ismingiz*\n\nTo'liq ism-familiyangizni yozing:\n_(Masalan: Karimov Ali Vohidovich)_",
        parse_mode="Markdown", reply_markup=kb_cancel_inline(),
    )
    return GET_NAME


async def _reg_start_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mocks = await db.get_active_mocks()
    if not mocks:
        await update.message.reply_text("📭 Hozircha ro'yxatdan o'tish uchun test yo'q.")
        return ConversationHandler.END
    if len(mocks) == 1:
        context.user_data["mock"] = mocks[0]
        await update.message.reply_text(
            "✍️ *1-qadam: Ismingiz*\n\nTo'liq ism-familiyangizni yozing:\n_(Masalan: Karimov Ali Vohidovich)_",
            parse_mode="Markdown", reply_markup=kb_cancel_inline(),
        )
        return GET_NAME
    await update.message.reply_text("📋 Qaysi testga ro'yxatdan o'tmoqchisiz?", reply_markup=kb_mocks(mocks))
    return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 5 or any(c.isdigit() for c in name):
        await update.message.reply_text(
            "❌ Iltimos, *to'liq* ism-familiyangizni yozing.\n_(Raqam bo'lmasin, kamida 5 harf)_",
            parse_mode="Markdown",
        )
        return GET_NAME
    context.user_data["full_name"] = name
    phone_kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📲 Raqamni avtomatik yuborish", request_contact=True)]],
        one_time_keyboard=True, resize_keyboard=True,
    )
    await update.message.reply_text(
        f"✅ Ism qabul qilindi: *{name}*\n\n"
        "📱 *2-qadam: Telefon raqam*\n\nRaqam ulashish tugmasini bosing yoki quyidagi ko'rinishda yozing:\n`+998901234567`",
        parse_mode="Markdown", reply_markup=phone_kb,
    )
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = validate_phone(update.message.text)
        if not phone:
            await update.message.reply_text(
                "❌ Raqam noto'g'ri.\nIltimos shunday yozing: `+998901234567`",
                parse_mode="Markdown",
            )
            return GET_PHONE
    context.user_data["phone"] = phone
    mock = context.user_data["mock"]
    await update.message.reply_text(
        "✅ Telefon raqami qabul qilindi!\n\n"
        f"📌 *{mock['title']}*\n"
        f"🗓 Sana: {mock['date_str']}\n"
        f"💰 Narx: *{mock['price']}*\n\n"
        "━━━━━━━━━━━━━━\n💳 *To'lov ma'lumotlari:*\n\n"
        f"🏦 Karta: `{PAYMENT_CARD}`\n"
        f"👤 Egasi: {PAYMENT_CARD_OWNER}\n"
        f"💵 Summa: *{mock['price']}*\n\n"
        "━━━━━━━━━━━━━━\n"
        "📸 *3-qadam:* To'lovni amalga oshirib, *chek rasmini* yuboring 👇",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove(),
    )
    return GET_RECEIPT


async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (update.message.photo or update.message.document):
        await update.message.reply_text(
            "❌ Iltimos, *to'lov cheki rasmini* yuboring.\n_(Ekran suratini yoki faylni yuboring)_",
            parse_mode="Markdown",
        )
        return GET_RECEIPT
    file_id = (
        update.message.photo[-1].file_id if update.message.photo
        else update.message.document.file_id
    )
    context.user_data["receipt"] = file_id
    d = context.user_data
    await update.message.reply_text(
        "📋 *Arizangizni tekshiring:*\n\n"
        + fmt_reg_summary({
            "full_name": d["full_name"], "phone": d["phone"],
            "mock_title": d["mock"]["title"], "mock_date": d["mock"]["date_str"],
            "price": d["mock"]["price"],
        })
        + "\n🧾 Chek: yuborildi ✅\n\nMa'lumotlar to'g'rimi?",
        parse_mode="Markdown", reply_markup=kb_confirm(),
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data != "confirm_yes":
        return ConversationHandler.END
    user = query.from_user
    d = context.user_data
    mock = d["mock"]
    reg_id = db.gen_reg_id()
    reg_data = {
        "id": reg_id, "mock_id": mock["id"], "mock_title": mock["title"],
        "mock_date": mock["date_str"], "user_tg_id": user.id,
        "username": user.username or "", "full_name": d["full_name"],
        "phone": d["phone"], "price": mock["price"],
        "receipt_file": d["receipt"], "status": "pending",
    }
    reg = await db.create_registration(reg_data)
    if not reg:
        await query.message.reply_text(
            "⚠️ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.\n/start",
            reply_markup=kb_main(user.id),
        )
        return ConversationHandler.END
    await query.message.reply_text(
        "🎉 *Arizangiz qabul qilindi!*\n\n"
        f"🆔 Raqam: `{reg_id}`\n\n"
        f"{fmt_reg_summary(reg_data)}\n\n"
        "⏳ Adminlar to'lovingizni tekshirib, sizga xabar yuborishadi.\n"
        "Odatda 30 daqiqa ichida! 😊",
        parse_mode="Markdown", reply_markup=kb_main(user.id),
    )
    try:
        await context.bot.send_photo(
            chat_id=APPROVAL_GROUP_ID,
            photo=d["receipt"],
            caption=fmt_group_msg(reg_data, user.username or ""),
            parse_mode="Markdown",
            reply_markup=kb_group_approval(reg_id),
        )
    except Exception:
        pass
    context.user_data.clear()
    return ConversationHandler.END


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=kb_main(update.effective_user.id))
    return ConversationHandler.END


async def _show_contact_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 Aloqa\n\n"
        f"🏫 {SCHOOL_NAME}\n"
        f"📱 Telefon raqami: {PHONE_CONTACT}\n"
        "💬 Telegram: @wxm\\_admin\n"
        "🕐 Ish vaqti: 9:00 \\- 18:00",
        parse_mode="MarkdownV2",
        reply_markup=kb_main(update.effective_user.id),
    )


async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        f"📞 Aloqa\n\n"
        f"🏫 {SCHOOL_NAME}\n"
        f"📱 Telefon raqami: {PHONE_CONTACT}\n"
        "💬 Telegram: @wxm\\_admin\n"
        "🕐 Ish vaqti: 9:00 \\- 18:00",
        parse_mode="MarkdownV2",
        reply_markup=kb_main(query.from_user.id),
    )


def build_user_conv() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(reg_start, pattern=r"^(reg_start|reg_mock\|.)$"),
            MessageHandler(
                filters.TEXT & filters.Regex(r"^✍️ Ro'yxatdan o'tish$"),
                _reg_start_msg,
            ),
        ],
        states={
            GET_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND
                    & ~filters.Regex(r"^(📋 Mock testlar|📞 Aloqa|⚙️ Admin panel)$"),
                    get_name,
                )
            ],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND
                    & ~filters.Regex(r"^(📋 Mock testlar|📞 Aloqa|⚙️ Admin panel)$"),
                    get_phone,
                ),
            ],
            GET_RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, get_receipt)],
            CONFIRM:     [CallbackQueryHandler(confirm, pattern=r"^confirm_yes$")],
        },
        fallbacks=[
            CommandHandler("cancel", cmd_cancel),
            CommandHandler("start",  cmd_start),
            CallbackQueryHandler(cmd_start, pattern=r"^back_noop$"),
        ],
        per_chat=True,
        per_user=True,
        per_message=False,
        allow_reentry=True,
        conversation_timeout=1800,
    )
