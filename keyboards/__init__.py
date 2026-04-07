from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import models
from constants import MINI_APP_LINK_TEXT, USEFUL_INFO_BUTTON, BACK_TO_SERVICES_BUTTON, PRICE_LIST_BUTTON, REVIEWS_BUTTON

# URL for Mini App
MINI_APP_URL = "https://sergey-zakhvatoshin.github.io/qos-miniapp/index.html"
PRICE_LIST_URL = "https://sergey-zakhvatoshin.github.io/qos-miniapp/index.html?page=price-list"
REVIEWS_URL = "https://sergey-zakhvatoshin.github.io/qos-miniapp/index.html?page=reviews"


# Create inline keyboard with beauty services
def get_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Manicure", callback_data="service_manicure")],
            [InlineKeyboardButton(text="Pedicure", callback_data="service_pedicure")],
            [InlineKeyboardButton(text="Eyelash Extensions", callback_data="service_eyelash")],
            [InlineKeyboardButton(text=USEFUL_INFO_BUTTON, callback_data="useful_info")],
            [InlineKeyboardButton(text="📋 My appointments", callback_data="my_appointments")],
        ]
    )
    return keyboard


# Create keyboard with useful information (Mini App)
def get_useful_info_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=MINI_APP_LINK_TEXT, web_app=WebAppInfo(url=MINI_APP_URL))],
            [InlineKeyboardButton(text=PRICE_LIST_BUTTON, web_app=WebAppInfo(url=PRICE_LIST_URL))],
            [InlineKeyboardButton(text=REVIEWS_BUTTON, web_app=WebAppInfo(url=REVIEWS_URL))],
            [InlineKeyboardButton(text=BACK_TO_SERVICES_BUTTON, callback_data="back_to_services")],
        ]
    )
    return keyboard


# Create inline keyboard with back button
def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to services", callback_data="back_to_services")],
        ]
    )
    return keyboard


# Create inline keyboard for booking another service or viewing appointments
def get_book_another_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 My appointments", callback_data="my_appointments")],
            [InlineKeyboardButton(text="Manicure", callback_data="service_manicure")],
            [InlineKeyboardButton(text="Pedicure", callback_data="service_pedicure")],
            [InlineKeyboardButton(text="Eyelash Extensions", callback_data="service_eyelash")],
        ]
    )
    return keyboard


# Create inline keyboard with available dates for next 7 days
def get_dates_keyboard(service: str, start_date: datetime = None, for_edit: bool = False, appt_id: int = None) -> InlineKeyboardMarkup:
    # Each button contains date and day of week
    if start_date is None:
        start_date = datetime.now()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Next 7 days including today
    for i in range(7):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_name = date.strftime("%A")[:3]  # First 3 letters (Mon, Tue, etc.)
        day_num = date.strftime("%d.%m.%Y")  # Format: 16.03.2026

        if for_edit:
            # For editing mode: date_edit_{appt_id}_{date}
            button = InlineKeyboardButton(
                text=f"{day_name} {day_num}",
                callback_data=f"date_edit_{appt_id}_{date_str}"
            )
        else:
            button = InlineKeyboardButton(
                text=f"{day_name} {day_num}",
                callback_data=f"date_{service}_{date_str}"
            )
        keyboard.inline_keyboard.append([button])

    # Add back button
    if for_edit:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⬅️ Back to appointments", callback_data="my_appointments")
        ])
    else:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⬅️ Back to services", callback_data="back_to_services")
        ])

    return keyboard


# Create inline keyboard with 4 time slots:
# 09:00-12:00, 12:00-15:00, 15:00-18:00, 18:00-21:00
def get_time_slots_keyboard(service: str, date: str) -> InlineKeyboardMarkup:
    time_slots = [
        ("09:00-12:00", "09:00-12:00"),
        ("12:00-15:00", "12:00-15:00"),
        ("15:00-18:00", "15:00-18:00"),
        ("18:00-21:00", "18:00-21:00"),
    ]

    # Get booked time slots for this service and date
    booked_slots = models.get_booked_time_slots(service, date)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for slot_id, slot_text in time_slots:
        # Skip already booked slots
        if slot_id in booked_slots:
            continue

        button = InlineKeyboardButton(
            text=slot_text,
            callback_data=f"time_{service}_{date}_{slot_id}"
        )
        keyboard.inline_keyboard.append([button])

    # Add back to dates button
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="⬅️ Back to dates", callback_data=f"dates_{service}")
    ])

    return keyboard


# Create keyboard with confirm and cancel buttons
def get_confirm_keyboard(service: str, date: str, time_slot: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{service}_{date}_{time_slot}")],
            [InlineKeyboardButton(text="✏️ Edit booking", callback_data=f"edit_booking_{service}_{date}_{time_slot}")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_{service}")],
        ]
    )
    return keyboard


# Create keyboard for canceling existing appointment
def get_cancel_appointment_keyboard(service: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes, cancel my appointment", callback_data=f"confirm_cancel_{service}")],
            [InlineKeyboardButton(text="No, keep it", callback_data=f"keep_appointment_{service}")],
        ]
    )
    return keyboard


# Create main menu keyboard after booking
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Book another service", callback_data="back_to_services")],
        ]
    )
    return keyboard


# Create keyboard for phone number request
def get_phone_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Send phone number", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


# Create empty keyboard (to hide reply keyboard)
def get_empty_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)


# Create edit booking menu keyboard
def get_edit_booking_keyboard(service: str, date: str, time_slot: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📌 Change service", callback_data=f"edit_service_{service}_{date}_{time_slot}")],
            [InlineKeyboardButton(text="📅 Change date/time", callback_data=f"edit_datetime_{service}_{date}_{time_slot}")],
            [InlineKeyboardButton(text="👤 Change name", callback_data=f"edit_name_{service}_{date}_{time_slot}")],
            [InlineKeyboardButton(text="📞 Change phone", callback_data=f"edit_phone_{service}_{date}_{time_slot}")],
            [InlineKeyboardButton(text="⬅️ Back to confirmation", callback_data=f"back_to_confirm_{service}_{date}_{time_slot}")],
        ]
    )
    return keyboard


# Create keyboard for viewing appointments with cancel/edit buttons
def get_appointments_keyboard(appointments: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for appt in appointments:
        service = appt["service"]
        date = appt["appointment_date"]
        time_slot = appt["time_slot"]
        appt_id = appt["id"]

        # Create buttons for each appointment
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"❌ Cancel {service.capitalize()}",
                callback_data=f"cancel_appt_{appt_id}"
            )
        ])
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"✏️ Edit {service.capitalize()}",
                callback_data=f"edit_appt_{appt_id}"
            )
        ])

    # Add back button
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="⬅️ Back to services", callback_data="back_to_services")
    ])

    return keyboard
