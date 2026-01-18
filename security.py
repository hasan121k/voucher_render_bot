import pytz
from datetime import datetime
from config import Config

def get_bd_time():
    """Returns current time object in Bangladesh timezone"""
    tz = pytz.timezone(Config.TIMEZONE)
    return datetime.now(tz)

def generate_dynamic_password():
    """Generates password: monirul + HHMM (BD Time)"""
    now = get_bd_time()
    time_str = now.strftime("%H%M")
    return f"monirul{time_str}"
