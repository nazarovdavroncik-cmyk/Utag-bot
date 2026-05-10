import json, os, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    Filters,
)

TOKEN = "8773184776:AAGKKfet4n4MvrYIiM32pjqSg79NIqxc3i4"
ADMIN_ID = 5764831373
CHANNEL = "@gaduza_channel"

DB = "db.json"

if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump({"users": {}, "groups": []}, f)

def load():
    with open(DB, "r") as f:
        return json.load(f)

def save(data):
    with open(DB, "w") as f:
        json.dump(data, f)

db = load()

def check_sub(bot, uid):
    try:
        x = bot.get_chat_member("@" + CHANNEL, uid)
        return x.status in ["member", "administrator", "creator"]
    except:
        return False

def start(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)

    if not check_sub(context.bot, update.effective_user.id):
        kb = [[InlineKeyboardButton("📢 Obuna", url=f"https://t.me/{CHANNEL}")]]
        update.message.reply_text(
            "Kanalga obuna bo‘ling",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    if uid not in db["users"]:
        db["users"][uid] = {"ball": 0, "bonus": 0}
        save(db)

    update.message.reply_text(
        "Bot ishladi ✅\n\n"
        "/bonus\n"
        "/me\n"
        "/top"
    )

def bonus(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    now = int(time.time())

    if now - db["users"][uid]["bonus"] < 86400:
        update.message.reply_text("24 soat kuting")
        return

    db["users"][uid]["ball"] += 2
    db["users"][uid]["bonus"] = now
    save(db)
    update.message.reply_text("+2 ball")

def me(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    b = db["users"][uid]["ball"]
    update.message.reply_text(f"Sizning ball: {b}")

def top(update: Update, context: CallbackContext):
    s = sorted(db["users"].items(),
               key=lambda x: x[1]["ball"],
               reverse=True)

    txt = "TOP\n"
    for i, (u, v) in enumerate(s[:10], 1):
        txt += f"{i}. {u} - {v['ball']}\n"

    update.message.reply_text(txt)

def anti_link(update: Update, context: CallbackContext):
    t = update.message.text.lower()
    if "http" in t or "t.me/" in t:
        try:
            update.message.delete()
            update.message.reply_text("Iltimos link tashlamang")
        except:
            pass

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("bonus", bonus))
dp.add_handler(CommandHandler("me", me))
dp.add_handler(CommandHandler("top", top))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, anti_link))

print("Bot ishladi ✅")
updater.start_polling()
updater.idle()
