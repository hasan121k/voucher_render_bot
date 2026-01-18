from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
import database as db
import threading
import bot
import time

app = Flask(__name__)
app.config.from_object(Config)

# ডাটাবেস ইনিশিয়াল করা
db.init_db()

# --- বট রান করা (ব্যাকগ্রাউন্ডে) ---
def run_bot():
    while True:
        try:
            print("Bot starting...")
            bot.bot.infinity_polling()
        except Exception as e:
            print(f"Bot Crash: {e}")
            time.sleep(5)

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# --- ওয়েব রাউট ---

def is_logged_in():
    return session.get('logged_in')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == Config.ADMIN_USERNAME and \
           request.form.get('password') == Config.ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong Username or Password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login'))
    
    vouchers = db.get_all_vouchers()
    stats = db.get_analytics()
    channel = db.get_channel_id()
    
    return render_template('dashboard.html', vouchers=vouchers, stats=stats, channel=channel)

@app.route('/create_voucher', methods=['POST'])
def create_voucher():
    if not is_logged_in(): return redirect(url_for('login'))
    
    minutes = request.form.get('minutes')
    max_use = request.form.get('max_use')
    custom_code = request.form.get('custom_code') # অ্যাডমিনের দেওয়া কোড
    
    if minutes and max_use:
        code, msg = db.create_voucher(minutes, max_use, custom_code)
        flash(f"{'Success: ' + code if code else msg}")
    
    return redirect(url_for('dashboard'))

@app.route('/toggle/<code>')
def toggle_voucher(code):
    if not is_logged_in(): return redirect(url_for('login'))
    db.toggle_pause_voucher(code)
    return redirect(url_for('dashboard'))

@app.route('/delete/<code>')
def delete_voucher(code):
    if not is_logged_in(): return redirect(url_for('login'))
    db.delete_voucher(code)
    return redirect(url_for('dashboard'))

@app.route('/set_channel', methods=['POST'])
def set_channel():
    if not is_logged_in(): return redirect(url_for('login'))
    db.set_channel_id(request.form.get('chat_id'))
    flash('Channel Updated')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
