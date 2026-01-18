import telebot
from config import Config
from security import generate_dynamic_password, get_bd_time
import database as db

bot = telebot.TeleBot(Config.BOT_TOKEN, threaded=False)

def check_channel_join(user_id):
    """চ্যানেল জয়েন চেক করা"""
    channel_id = db.get_channel_id()
    if not channel_id:
        return True
    try:
        status = bot.get_chat_member(channel_id, user_id).status
        if status in ['creator', 'administrator', 'member']:
            return True
        return False
    except:
        return True # বট এডমিন না হলে বাইপাস করবে

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Please send your **Voucher Code** to get access.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_voucher_code(message):
    code_text = message.text.strip() # ইউজার যা লিখেছে (যেমন: 1702297)
    user_id = message.from_user.id
    
    # ১. চ্যানেল চেক
    if not check_channel_join(user_id):
        channel_id = db.get_channel_id()
        bot.reply_to(message, f"⚠️ You must join our channel first!\nChannel ID: {channel_id}\n\nJoin and try again.")
        return

    # ২. ডাটাবেসে কোড চেক করা
    voucher = db.get_voucher(code_text)
    
    if not voucher:
        bot.reply_to(message, "❌ **Invalid Code.** Please try again.", parse_mode="Markdown")
        return

    # ভাউচার ডাটা নেওয়া
    expire_ts = voucher['expire_timestamp']
    max_use = voucher['max_use']
    used_count = voucher['used_count']
    paused = voucher['paused']
    
    # ৩. ভ্যালিডেশন
    current_ts = get_bd_time().timestamp()

    if paused:
        bot.reply_to(message, "⏸️ This code is currently **paused** by admin.", parse_mode="Markdown")
        return
    
    if current_ts > expire_ts:
        bot.reply_to(message, "⏰ This code has **expired**.", parse_mode="Markdown")
        return

    if used_count >= max_use:
        bot.reply_to(message, "🚫 Usage limit **exceeded** for this code.", parse_mode="Markdown")
        return

    # ৪. সব ঠিক থাকলে - পাসওয়ার্ড দেওয়া
    db.redeem_voucher_db(code_text, user_id)
    dynamic_pass = generate_dynamic_password()
    
    response = (
        f"✅ **Access Granted!**\n\n"
        f"🎫 Code: `{code_text}`\n"
        f"🔐 Password: `{dynamic_pass}`\n"
        f"⏳ Valid for limited time."
    )
    
    bot.reply_to(message, response, parse_mode="Markdown")
