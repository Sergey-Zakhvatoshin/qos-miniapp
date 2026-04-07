import os
import re
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def format_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to DD.MM.YYYY"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%d.%m.%Y")


def validate_phone(phone: str) -> bool:
    """Validate phone format: 8 XXX XXX XX XX or +7 XXX XXX XX XX (with spaces)"""
    pattern = r"^(\+?7|8)\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}$"
    return bool(re.match(pattern, phone))


def format_phone(phone: str) -> str:
    """Format phone to standard format: 8 XXX XXX XX XX"""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and (digits.startswith("8") or digits.startswith("7")):
        return f"8 {digits[1:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"
    return phone
