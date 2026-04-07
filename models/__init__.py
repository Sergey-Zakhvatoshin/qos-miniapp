import sqlite3
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

DATABASE = "appointments.db"


# Get database connection
def get_connection():
    db_path = os.path.abspath(DATABASE)
    logger.info(f"Using database: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# Initialize database tables
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            appointment_date DATE NOT NULL,
            time_slot TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, service, appointment_date, time_slot)
        )
    """)

    # Create reminders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(appointment_id, reminder_type)
        )
    """)

    # Create review_requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS review_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL UNIQUE,
            telegram_id INTEGER NOT NULL,
            service TEXT NOT NULL,
            name TEXT,
            date TEXT,
            time_slot TEXT,
            rating INTEGER,
            review_text TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responded_at TIMESTAMP,
            UNIQUE(appointment_id)
        )
    """)

    conn.commit()
    conn.close()


# Create new user or update existing user info
def create_or_update_user(telegram_id: int, username: str = None, first_name: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
    """, (telegram_id, username, first_name))

    conn.commit()
    user_id = cursor.lastrowid

    # Get actual user_id if user already existed
    if cursor.rowcount == 0:
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        user_id = cursor.fetchone()[0]

    conn.close()
    return user_id


# Get user by telegram ID
def get_user_by_telegram_id(telegram_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    conn.close()
    return user


# Check if user has existing appointment for the same service
def check_existing_appointment(telegram_id: int, service: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM appointments
        WHERE telegram_id = ? AND service = ? AND appointment_date >= DATE('now')
    """, (telegram_id, service))

    appointment = cursor.fetchone()
    conn.close()
    return appointment


# Get all appointments for a user
def get_user_appointments(telegram_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM appointments
        WHERE telegram_id = ?
        ORDER BY appointment_date, time_slot
    """, (telegram_id,))

    appointments = cursor.fetchall()
    conn.close()
    return appointments


# Get future appointments for a user (only upcoming appointments)
def get_future_appointments(telegram_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Getting future appointments for telegram_id={telegram_id}, today={today}")

    cursor.execute("""
        SELECT *
        FROM appointments
        WHERE telegram_id = ? AND appointment_date >= ?
        ORDER BY appointment_date, time_slot
    """, (telegram_id, today))

    appointments = cursor.fetchall()
    logger.info(f"Found {len(appointments)} future appointments: {[dict(a) for a in appointments]}")
    conn.close()
    return appointments


# Create new appointment with client name and phone
def create_appointment(telegram_id: int, service: str, appointment_date: str, time_slot: str, name: str, phone: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO appointments (telegram_id, service, appointment_date, time_slot, name, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (telegram_id, service, appointment_date, time_slot, name, phone))

        conn.commit()
        success = True
        appointment_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        success = False
        appointment_id = None

    conn.close()
    return success, appointment_id


# Cancel appointment for a specific service
def cancel_appointment(telegram_id: int, service: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM appointments
        WHERE telegram_id = ? AND service = ?
    """, (telegram_id, service))

    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted


# Cancel appointment by ID
def cancel_appointment_by_id(telegram_id: int, appointment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    logger.info(f"Deleting appointment: id={appointment_id}")

    cursor.execute("""
        DELETE FROM appointments
        WHERE id = ?
    """, (appointment_id,))

    conn.commit()

    deleted = cursor.rowcount > 0

    logger.info(f"Delete result: deleted={deleted}, rows_affected={cursor.rowcount}")

    conn.close()

    return deleted


# Get appointment by ID and telegram_id
def get_appointment_by_id(telegram_id: int, appointment_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM appointments
        WHERE id = ? AND telegram_id = ?
    """, (appointment_id, telegram_id))

    appointment = cursor.fetchone()
    conn.close()
    return appointment


# Check if time slot is available for any user
def is_time_slot_available(service: str, appointment_date: str, time_slot: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM appointments
        WHERE service = ? AND appointment_date = ? AND time_slot = ?
    """, (service, appointment_date, time_slot))

    count = cursor.fetchone()[0]
    conn.close()

    return count == 0


# Get all booked time slots for a specific service and date
def get_booked_time_slots(service: str, appointment_date: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT time_slot FROM appointments
        WHERE service = ? AND appointment_date = ?
    """, (service, appointment_date))

    booked_slots = [row["time_slot"] for row in cursor.fetchall()]
    conn.close()

    return booked_slots


# Get appointments for tomorrow (for reminder notifications)
def get_tomorrow_appointments():
    """Get all appointments scheduled for tomorrow"""
    conn = get_connection()
    cursor = conn.cursor()

    tomorrow = (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT *
        FROM appointments
        WHERE appointment_date = ?
        ORDER BY appointment_date, time_slot
    """, (tomorrow,))

    appointments = cursor.fetchall()
    logger.info(f"Found {len(appointments)} appointments for tomorrow ({tomorrow})")
    conn.close()
    return [dict(a) for a in appointments]


# Check if reminder was already sent for an appointment
def is_reminder_sent(appointment_id: int, reminder_type: str = "24h") -> bool:
    """Check if reminder was already sent for this appointment"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM reminders
        WHERE appointment_id = ? AND reminder_type = ?
    """, (appointment_id, reminder_type))

    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


# Mark reminder as sent
def mark_reminder_sent(appointment_id: int, reminder_type: str = "24h"):
    """Mark reminder as sent in database"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO reminders (appointment_id, reminder_type)
            VALUES (?, ?)
        """, (appointment_id, reminder_type))
        conn.commit()
        logger.info(f"Marked reminder {reminder_type} as sent for appointment {appointment_id}")
    except sqlite3.IntegrityError:
        # Already exists, that's fine
        pass
    finally:
        conn.close()


# Review requests functions

def create_review_request(appointment_id: int, telegram_id: int, service: str):
    """Create a new review request record"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO review_requests (appointment_id, telegram_id, service)
            VALUES (?, ?, ?)
        """, (appointment_id, telegram_id, service))
        conn.commit()
        logger.info(f"Created review request for appointment {appointment_id}")
        return True
    except sqlite3.IntegrityError:
        logger.debug(f"Review request already exists for appointment {appointment_id}")
        return False
    finally:
        conn.close()


def mark_review_request_sent(appointment_id: int):
    """Mark that a review request was already sent for this appointment"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO review_requests (appointment_id, telegram_id, service)
            SELECT id, telegram_id, service FROM appointments WHERE id = ?
        """, (appointment_id,))
        conn.commit()
    finally:
        conn.close()


def is_review_request_sent(appointment_id: int) -> bool:
    """Check if review request was already sent for this appointment"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM review_requests WHERE appointment_id = ?
    """, (appointment_id,))

    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def save_review_rating(appointment_id: int, rating: int, review_text: str = None):
    """Save review rating and optional text"""
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE review_requests
        SET rating = ?, review_text = ?, responded_at = ?
        WHERE appointment_id = ?
    """, (rating, review_text, datetime.now(), appointment_id))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def get_pending_reviews() -> list:
    """Get appointments that need review requests (past appointments without review requests)"""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT a.*, r.id as review_id
        FROM appointments a
        LEFT JOIN review_requests r ON a.id = r.appointment_id
        WHERE a.appointment_date < ?
        AND r.id IS NULL
        AND a.appointment_date >= DATE(?, '-7 days')
        ORDER BY a.appointment_date, a.time_slot
    """, (today, today))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def save_review_request_data(appointment_id: int, name: str = None, date: str = None, time_slot: str = None):
    """Save additional data for review request"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE review_requests
        SET name = ?, date = ?, time_slot = ?
        WHERE appointment_id = ?
    """, (name, date, time_slot, appointment_id))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def get_review_request_data(telegram_id: int) -> dict:
    """Get review request data for a user"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM review_requests
        WHERE telegram_id = ?
        AND rating IS NULL
        ORDER BY requested_at DESC
        LIMIT 1
    """, (telegram_id,))

    row = cursor.fetchone()
    result = dict(row) if row else None
    conn.close()
    return result
