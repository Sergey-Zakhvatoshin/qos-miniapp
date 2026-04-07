import asyncio
import logging
from datetime import datetime, timedelta
from config import bot
from models import is_reminder_sent, mark_reminder_sent, get_pending_reviews, is_review_request_sent
from config import format_date


logger = logging.getLogger(__name__)


def get_appointment_datetime(appt: dict) -> datetime:
    """Parse appointment date and time slot to datetime"""
    date_str = appt["appointment_date"]
    time_slot = appt["time_slot"]
    start_time_str = time_slot.split("-")[0]  # "15:00" from "15:00-18:00"
    hour, minute = map(int, start_time_str.split(":"))
    
    appt_datetime = datetime.strptime(date_str, "%Y-%m-%d")
    appt_datetime = appt_datetime.replace(hour=hour, minute=minute)
    return appt_datetime


async def send_reminder(appt: dict, reminder_type: str, hours_before: int):
    """Send reminder for a specific appointment"""
    appt_id = appt["id"]
    
    # Skip if already sent
    if is_reminder_sent(appt_id, reminder_type):
        logger.debug(f"Reminder {reminder_type} already sent for appointment {appt_id}")
        return False
    
    now = datetime.now()
    appt_datetime = get_appointment_datetime(appt)
    reminder_time = appt_datetime - timedelta(hours=hours_before)
    
    # Check if it's time to send (within 5 minutes of reminder time)
    time_diff = (now - reminder_time).total_seconds()
    if not (-300 <= time_diff <= 300):  # Within 5 minutes window
        return False
    
    try:
        telegram_id = appt["telegram_id"]
        service = appt["service"].capitalize()
        date = format_date(appt["appointment_date"])
        time_slot = appt["time_slot"]
        name = appt["name"]
        
        if hours_before >= 24:
            reminder_text = (
                f"🔔 <b>Reminder: Your appointment is in {hours_before} hours!</b>\n\n"
                f"📌 Service: <b>{service}</b>\n"
                f"📅 Date: <b>{date}</b>\n"
                f"⏰ Time: <b>{time_slot}</b>\n"
                f"👤 Name: <b>{name}</b>\n\n"
                f"We look forward to seeing you!"
            )
        else:
            reminder_text = (
                f"🔔 <b>Reminder: Your appointment is today in {hours_before} hours!</b>\n\n"
                f"📌 Service: <b>{service}</b>\n"
                f"📅 Date: <b>{date}</b>\n"
                f"⏰ Time: <b>{time_slot}</b>\n"
                f"👤 Name: <b>{name}</b>\n\n"
                f"See you soon!"
            )
        
        await bot.send_message(
            chat_id=telegram_id,
            text=reminder_text,
            parse_mode="HTML",
        )
        logger.info(f"Reminder {reminder_type} sent to telegram_id={telegram_id} for appointment {appt_id}")
        
        # Mark as sent in database
        mark_reminder_sent(appt_id, reminder_type)
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reminder {reminder_type} for appointment {appt_id}: {e}")
        return False


async def send_reminders():
    """Send reminder notifications 24 hours and 2 hours before appointment"""
    logger.info("Running reminder scheduler...")

    # Get all future appointments
    import sqlite3
    db_path = "appointments.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    now = datetime.now()

    # Get appointments for today and tomorrow (for 24h and 2h reminders)
    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (now + timedelta(days=2)).strftime("%Y-%m-%d")

    # Get appointments for today (for 2h reminders) and tomorrow (for 24h reminders)
    cursor = conn.execute("""
        SELECT * FROM appointments
        WHERE appointment_date IN (?, ?, ?)
        ORDER BY appointment_date, time_slot
    """, (today, tomorrow, day_after))

    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not appointments:
        logger.info("No upcoming appointments, skipping reminders")
    else:
        for appt in appointments:
            # Send 24-hour reminder
            await send_reminder(appt, "24h", 24)

            # Send 2-hour reminder
            await send_reminder(appt, "2h", 2)

        logger.info(f"Reminder scheduler completed.")

    # Send review requests for past appointments
    await send_review_requests()


async def send_review_requests():
    """Send review requests for appointments that happened ~24 hours ago"""
    logger.info("Running review request scheduler...")

    pending = get_pending_reviews()

    if not pending:
        logger.info("No pending review requests")
        return

    for appt in pending:
        appointment_id = appt["id"]
        telegram_id = appt["telegram_id"]
        service = appt["service"]
        appt_date = appt["appointment_date"]
        time_slot = appt["time_slot"]

        # Check if already sent
        if is_review_request_sent(appointment_id):
            logger.debug(f"Review request already sent for appointment {appointment_id}")
            continue

        # Calculate appointment end time (approximate)
        appt_datetime = datetime.strptime(appt_date, "%Y-%m-%d")
        start_hour = int(time_slot.split("-")[0].split(":")[0])
        appt_datetime = appt_datetime.replace(hour=start_hour)

        # Check if ~24 hours have passed since appointment
        now = datetime.now()
        time_since_appt = (now - appt_datetime).total_seconds() / 3600  # in hours

        # Send if between 20-28 hours after appointment (5-hour window)
        if 20 <= time_since_appt <= 28:
            logger.info(f"Sending review request for appointment {appointment_id} ({time_since_appt:.1f}h after)")
            from handlers.reviews_handlers import send_rating_request
            await send_rating_request(
                telegram_id,
                service,
                appointment_id,
                name=appt.get("name"),
                date=appt.get("appointment_date"),
                time_slot=appt.get("time_slot"),
            )

    logger.info(f"Review request scheduler completed. Processed {len(pending)} appointments.")


async def schedule_reminders():
    """Run reminder scheduler every 5 minutes"""
    while True:
        try:
            await send_reminders()
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")

        # Check every 5 minutes
        await asyncio.sleep(300)
