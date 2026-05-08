from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8773184776:AAGKKfet4n4MvrYIiM32pjqSg79NIqxc3i4"
ADMIN_ID = 5764831373
CHANNEL_USERNAME = "@gaduza_mafia1"   # @ belgisisiz yozing

users = set()
groups = set()

admin_keyboard = ReplyKeyboardMarkup(
    [
        ["📊 Statistika", "👥 Guruhlar"],
        ["📢 Tarqatish"]
    ],
    resize_keyboard=True
)

async def check_sub(user_id, bot):
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",
            user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    sub = await check_sub(user_id, context.bot)
    if not sub:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Kanalga kirish", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
        ])
        return await update.message.reply_text(
            "Botdan foydalanish uchun kanalga obuna bo‘ling.",
            reply_markup=kb
        )

    users.add(user_id)

    if user_id == ADMIN_ID:
        await update.message.reply_text("Admin panel ✅", reply_markup=admin_keyboard)
    else:
        await update.message.reply_text("Bot ishlayapti ✅")

async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    sub = await check_sub(user_id, context.bot)

    if sub:
        users.add(user_id)
        if user_id == ADMIN_ID:
            await query.message.reply_text("Admin panel ✅", reply_markup=admin_keyboard)
        else:
            await query.message.reply_text("Botga xush kelibsiz ✅")
    else:
        await query.message.reply_text("Hali kanalga obuna bo‘lmagansiz ❌")

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "📊 Statistika":
        await update.message.reply_text(f"👥 Userlar: {len(users)}")

    elif text == "👥 Guruhlar":
        await update.message.reply_text(f"📢 Guruhlar: {len(groups)}")

    elif text == "📢 Tarqatish":
        await update.message.reply_text("Yuborish: /send salom")

async def sendall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return await update.message.reply_text("Xabar kiriting")

    msg = " ".join(context.args)
    sent = 0

    for user in users:
        try:
            await context.bot.send_message(user, msg)
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ {sent} userga yuborildi")

async def group_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        groups.add(chat.id)
        await update.message.reply_text("✅ Guruh bazaga qo‘shildi")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("send", sendall))
app.add_handler(CallbackQueryHandler(check_button, pattern="check_sub"))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_added))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, panel))

print("Bot ishga tushdi ✅")
app.run_polling()
