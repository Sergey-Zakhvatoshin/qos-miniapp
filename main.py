import asyncio
import logging
from config import bot, dp
from handlers import (
    start_handlers,
    booking_handlers,
    edit_handlers,
    appointments_handlers,
    reviews_handlers,
)
from models import init_db
from scheduler import schedule_reminders
from aiogram.exceptions import TelegramBadRequest


async def main():
    try:
        # Verify bot token and initialize
        init_db()
        logging.info("Database initialized")

        bot_info = await bot.get_me()
        logging.info(f"Bot started: @{bot_info.username}")

        # Start reminder scheduler in background
        asyncio.create_task(schedule_reminders())
        logging.info("Reminder scheduler started")

        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.debug("Ignored 'message is not modified' error")
        else:
            logging.error(f"Telegram error: {e}")
    except Exception as e:
        logging.error(f"Bot error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
