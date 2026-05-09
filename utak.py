import json, os, random, time
from telegram import *
from telegram.ext import *

TOKEN="8773184776:AAGKKfet4n4MvrYIiM32pjqSg79NIqxc3i4"
ADMIN_ID=5764831373
CHANNEL="@gaduza_channel"
LOG="@gaduza_logs"

dbfile="db.json"

if not os.path.exists(dbfile):
    json.dump({"users":{},"groups":[]}, open(dbfile,"w"))

def load():
    return json.load(open(dbfile))

def save(x):
    json.dump(x, open(dbfile,"w"))

db=load()

async def check_sub(uid, bot):
    try:
        x=await bot.get_chat_member(f"@{CHANNEL}", uid)
        return x.status in ["member","administrator","creator"]
    except:
        return False

async def start(update, context):
    u=update.effective_user
    uid=str(u.id)

    if not await check_sub(u.id, context.bot):
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Obuna", url=f"https://t.me/{CHANNEL}")]
        ])
        return await update.message.reply_text("Kanalga obuna bo‘ling", reply_markup=kb)

    if uid not in db["users"]:
        db["users"][uid]={"ball":0,"ref":0,"bonus":0}
        if context.args:
            ref=context.args[0]
            if ref in db["users"] and ref!=uid:
                db["users"][ref]["ball"]+=5
                db["users"][ref]["ref"]+=1
        save(db)

    link=f"https://t.me/{context.bot.username}?start={uid}"

    await update.message.reply_text(
f"""Salom ✅
Referral linkingiz:
{link}

Buyruqlar:
/bonus
/top
/me"""
    )

async def bonus(update, context):
    uid=str(update.effective_user.id)
    now=int(time.time())

    if now-db["users"][uid]["bonus"]<86400:
        return await update.message.reply_text("24 soat kuting")

    db["users"][uid]["ball"]+=2
    db["users"][uid]["bonus"]=now
    save(db)
    await update.message.reply_text("+2 ball")

async def me(update, context):
    uid=str(update.effective_user.id)
    u=db["users"][uid]
    await update.message.reply_text(
        f"Ball: {u['ball']}\nReferral: {u['ref']}"
    )

async def top(update, context):
    s=sorted(db["users"].items(),
             key=lambda x:x[1]["ball"],
             reverse=True)[:10]

    txt="TOP 10\n"
    for i,(k,v) in enumerate(s,1):
        txt+=f"{i}. {k} - {v['ball']}\n"

    await update.message.reply_text(txt)

async def refresh(update, context):
    if update.effective_chat.type in ["group","supergroup"]:
        if update.effective_chat.id not in db["groups"]:
            db["groups"].append(update.effective_chat.id)
            save(db)
        await update.message.reply_text("Refresh bo‘ldi ✅")

async def welcome(update, context):
    if update.my_chat_member:
        chat=update.effective_chat
        if chat.id not in db["groups"]:
            db["groups"].append(chat.id)
            save(db)

        await context.bot.send_message(
            chat.id,
"""Assalomu alaykum
Gaduza utak botini guruhga qo‘shganingiz uchun rahmat

Utak boshlash:
/refresh

/r premium
/s oddiy

Admin: @gaduza2687"""
        )

async def anti_link(update, context):
    if "http" in update.message.text or "t.me/" in update.message.text:
        try:
            await update.message.delete()
            await update.message.reply_text(
                "Iltimos guruhga reklama qilmang"
            )
        except:
            pass

app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("bonus",bonus))
app.add_handler(CommandHandler("top",top))
app.add_handler(CommandHandler("me",me))
app.add_handler(CommandHandler("refresh",refresh))

app.add_handler(ChatMemberHandler(
    welcome,
    ChatMemberHandler.MY_CHAT_MEMBER
))

app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    anti_link
))

print("Bot ishladi ✅")
app.run_polling()
