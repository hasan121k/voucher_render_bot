import sqlite3
import random
import string
from datetime import timedelta
from config import Config
from security import get_bd_time

def get_db_connection():
    conn = sqlite3.connect(Config.DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # ভাউচার টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS vouchers (
        code TEXT PRIMARY KEY,
        expire_timestamp REAL,
        max_use INTEGER,
        used_count INTEGER DEFAULT 0,
        active BOOLEAN DEFAULT 1,
        paused BOOLEAN DEFAULT 0
    )''')
    
    # ইউজার লগ টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        voucher_code TEXT,
        redeemed_at TEXT
    )''')
    
    # সেটিংস টেবিল (চ্যানেল চেকের জন্য)
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    conn.commit()
    conn.close()

# --- Voucher Operations ---

def create_voucher(minutes, max_use, custom_code=None):
    """
    custom_code: যদি অ্যাডমিন নিজে কোড দেয় (যেমন 1702297)
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # ১. কোড ঠিক করা (কাস্টম নাকি অটো)
    if custom_code and custom_code.strip():
        code = custom_code.strip()
    else:
        # র‍্যান্ডম ৬ সংখ্যার কোড
        code = ''.join(random.choices(string.digits, k=6))
    
    # ২. মেয়াদ ঠিক করা
    now = get_bd_time()
    expire_time = now + timedelta(minutes=int(minutes))
    expire_timestamp = expire_time.timestamp()
    
    try:
        c.execute("INSERT INTO vouchers (code, expire_timestamp, max_use) VALUES (?, ?, ?)",
                  (code, expire_timestamp, max_use))
        conn.commit()
        return code, "Success"
    except sqlite3.IntegrityError:
        # যদি এই কোড আগেই থাকে
        if custom_code:
            return None, "Error: This code already exists!"
        else:
            conn.close()
            return create_voucher(minutes, max_use) # অটো হলে আবার ট্রাই করবে
    finally:
        conn.close()

def get_voucher(code):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vouchers WHERE code = ?", (code,))
    voucher = c.fetchone()
    conn.close()
    return voucher

def redeem_voucher_db(code, user_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # ইউজার লগ রাখা
    bd_time = get_bd_time().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO users (user_id, voucher_code, redeemed_at) VALUES (?, ?, ?)", 
              (user_id, code, bd_time))
    
    # ব্যবহার সংখ্যা বাড়ানো
    c.execute("UPDATE vouchers SET used_count = used_count + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()

# --- Admin Helper Functions ---

def get_all_vouchers():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vouchers ORDER BY expire_timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def toggle_pause_voucher(code):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE vouchers SET paused = NOT paused WHERE code = ?", (code,))
    conn.commit()
    conn.close()

def delete_voucher(code):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vouchers WHERE code = ?", (code,))
    conn.commit()
    conn.close()

def get_analytics():
    conn = get_db_connection()
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM vouchers").fetchone()[0]
    active = c.execute("SELECT COUNT(*) FROM vouchers WHERE active=1 AND paused=0").fetchone()[0]
    paused = c.execute("SELECT COUNT(*) FROM vouchers WHERE paused=1").fetchone()[0]
    redeemed = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return {"total": total, "active": active, "paused": paused, "redeemed": redeemed}

def set_channel_id(chat_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('required_channel', ?)", (chat_id,))
    conn.commit()
    conn.close()

def get_channel_id():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='required_channel'")
    row = c.fetchone()
    conn.close()
    return row['value'] if row else None
