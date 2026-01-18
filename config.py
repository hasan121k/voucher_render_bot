import os

class Config:
    # Render Environment Variables
    PORT = int(os.environ.get("PORT", 5000))
    BOT_TOKEN = os.environ.get("8548324259:AAGnYwHCML7aNQN0qfEzwBVChRSrZTtTKz0")
    
    # Admin Credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "admin123")
    
    # App Config
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_secret_key")
    TIMEZONE = 'Asia/Dhaka'
    DB_NAME = "data.db"
