import logging
import smtplib
from email.mime.text import MIMEText
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import dp, bot
from constants import (
    REVIEW_REQUEST_TITLE,
    REVIEW_REQUEST_TEXT,
    REVIEW_RATING_PROMPT,
    REVIEW_TEXT_PROMPT,
    REVIEW_POSITIVE_THANKS,
    REVIEW_POSITIVE_LINK,
    REVIEW_NEGATIVE_THANKS,
    ADMIN_REVIEW_SUBJECT,
    ADMIN_REVIEW_BODY,
    YANDEX_MAPS_LINK,
)
from states import ReviewState
import models
from config import format_date
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def get_rating_keyboard(appointment_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with rating buttons 1-5"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ 1", callback_data=f"review_rate_1_{appointment_id}"),
                InlineKeyboardButton(text="⭐⭐ 2", callback_data=f"review_rate_2_{appointment_id}"),
                InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data=f"review_rate_3_{appointment_id}"),
                InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data=f"review_rate_4_{appointment_id}"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data=f"review_rate_5_{appointment_id}"),
            ]
        ]
    )
    return keyboard


def get_yandex_maps_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with Yandex Maps link"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=REVIEW_POSITIVE_LINK, url=YANDEX_MAPS_LINK)]
        ]
    )
    return keyboard


async def send_rating_request(telegram_id: int, service: str, appointment_id: int, name: str = None, date: str = None, time_slot: str = None):
    """Send a review request to a user"""
    try:
        logger.info(f"Attempting to send review request: telegram_id={telegram_id}, appointment_id={appointment_id}, service={service}")

        # Check if already sent
        if models.is_review_request_sent(appointment_id):
            logger.warning(f"Review request already sent for appointment {appointment_id}, skipping")
            return False

        # Mark as sent
        models.mark_review_request_sent(appointment_id)
        logger.info(f"Marked review request as sent for appointment {appointment_id}")

        # Build message
        text = (
            REVIEW_REQUEST_TITLE + "\n\n"
            + REVIEW_REQUEST_TEXT.format(service=service.capitalize()) + "\n\n"
            + REVIEW_RATING_PROMPT
        )
        keyboard = get_rating_keyboard(appointment_id)

        logger.info(f"Sending message to telegram_id={telegram_id}")
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

        logger.info(f"Review request sent successfully to telegram_id={telegram_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send review request for appointment {appointment_id}: {e}", exc_info=True)
        return False


async def send_admin_email(service: str, rating: int, name: str, telegram_id: int, date: str, time_slot: str, review_text: str):
    """Send email notification to admin about negative review"""
    admin_email = os.getenv("ADMIN_EMAIL")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not admin_email or not smtp_server:
        logger.warning("Email configuration missing, skipping admin notification")
        return

    try:
        subject = ADMIN_REVIEW_SUBJECT.format(service=service.capitalize())
        body = ADMIN_REVIEW_BODY.format(
            service=service.capitalize(),
            rating=rating,
            name=name,
            telegram_id=telegram_id,
            date=date,
            time_slot=time_slot,
            review_text=review_text or "No text provided",
        )

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = smtp_user or smtp_server
        msg["To"] = admin_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Admin email sent for negative review (appointment service: {service})")

    except Exception as e:
        logger.error(f"Failed to send admin email: {e}")


# Handle rating selection: review_rate_{rating}_{appointment_id}
@dp.callback_query(F.data.startswith("review_rate_"))
async def process_rating_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Parse: review_rate_5_123
    parts = callback_query.data.split("_")
    rating = int(parts[2])
    appointment_id = int(parts[3])

    # Get appointment data from DB
    appt = models.get_appointment_by_id(callback_query.from_user.id, appointment_id)
    if not appt:
        await callback_query.answer("Appointment not found", show_alert=True)
        return

    # Convert to dict if needed
    if hasattr(appt, 'keys'):
        appt = dict(appt)

    # Store data in state for review text handler
    await state.update_data(
        rating=rating,
        appointment_id=appointment_id,
        service=appt["service"],
        name=appt["name"],
        date=appt["appointment_date"],
        time_slot=appt["time_slot"],
    )
    await state.set_state(ReviewState.waiting_for_review_text)

    # Ask for review text
    await callback_query.message.answer(
        REVIEW_TEXT_PROMPT,
        parse_mode="HTML",
    )

    await callback_query.answer()


# Handle review text input
@dp.message(ReviewState.waiting_for_review_text)
async def process_review_text(message: types.Message, state: FSMContext):
    review_text = message.text.strip()

    # Check if user wants to skip
    if review_text.lower() == "skip":
        review_text = None

    # Get data from state
    data = await state.get_data()
    rating = data.get("rating")
    appointment_id = data.get("appointment_id")
    service = data.get("service")
    name = data.get("name")
    date = data.get("date")
    time_slot = data.get("time_slot")

    if not rating or not appointment_id:
        await message.answer("Session expired. Please start again.")
        await state.clear()
        return

    # Save review to database
    models.save_review_rating(appointment_id, rating, review_text)

    # Handle based on rating
    if rating >= 4:
        # Positive review - thank and offer Yandex Maps link
        await message.answer(
            REVIEW_POSITIVE_THANKS,
            parse_mode="HTML",
            reply_markup=get_yandex_maps_keyboard(),
        )
    else:
        # Negative review - thank and notify admin
        await message.answer(
            REVIEW_NEGATIVE_THANKS,
            parse_mode="HTML",
        )

        # Send email to admin
        await send_admin_email(
            service=service,
            rating=rating,
            name=name,
            telegram_id=message.from_user.id,
            date=format_date(date),
            time_slot=time_slot,
            review_text=review_text or "No text provided",
        )

    await state.clear()
