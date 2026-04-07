import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import dp, format_date
from keyboards import (
    get_back_keyboard,
    get_appointments_keyboard,
    get_book_another_keyboard,
    get_services_keyboard,
    get_dates_keyboard,
)
from constants import BOOK_ANOTHER_MESSAGE, WELCOME_MESSAGE
from states import BookingState
import models


# Handle back to services button
@dp.callback_query(lambda c: c.data == "back_to_services")
async def process_back_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback_query.message.answer(
        BOOK_ANOTHER_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_book_another_keyboard(),
    )
    await callback_query.answer()


# Handle back to dates button
@dp.callback_query(lambda c: c.data.startswith("dates_"))
async def process_back_to_dates_callback(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.replace("dates_", "")

    await callback_query.message.answer(
        "Please select a date for your appointment:",
        reply_markup=get_dates_keyboard(service),
    )
    await callback_query.answer()


# Handle "My appointments" button
@dp.callback_query(lambda c: c.data == "my_appointments")
async def process_my_appointments_callback(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id

    # Get future appointments
    appointments = models.get_future_appointments(telegram_id)

    if not appointments:
        logging.info(f"No appointments for telegram_id={telegram_id}")
        await callback_query.message.answer(
            "You have no upcoming appointments.\n\n"
            "Use the button below to book a new service.",
            parse_mode="HTML",
            reply_markup=get_back_keyboard(),
        )
    else:
        # Show all appointments with cancel/edit buttons
        appointments_text = "📋 <b>Your upcoming appointments:</b>\n\n"

        for appt in appointments:
            date_formatted = format_date(appt["appointment_date"])
            appointments_text += (
                f"📌 <b>{appt['service'].capitalize()}</b>\n"
                f"📅 Date: {date_formatted}\n"
                f"⏰ Time: {appt['time_slot']}\n"
                f"👤 Name: {appt['name']}\n"
                f"📞 Phone: {appt['phone']}\n\n"
            )

        logging.info(f"Showing {len(appointments)} appointments with cancel/edit buttons")
        await callback_query.message.answer(
            appointments_text,
            parse_mode="HTML",
            reply_markup=get_appointments_keyboard(appointments),
        )

    await callback_query.answer()


# Handle cancel appointment from my appointments
@dp.callback_query(lambda c: c.data.startswith("cancel_appt_"))
async def process_cancel_appt_callback(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    appointment_id = int(callback_query.data.replace("cancel_appt_", ""))

    logging.info(f"Cancel requested: appt_id={appointment_id}, telegram_id={telegram_id}")

    # Get appointment to show details
    appointment = models.get_appointment_by_id(telegram_id, appointment_id)

    if not appointment:
        logging.warning(f"Appointment not found: appt_id={appointment_id}")
        await callback_query.message.answer(
            "Appointment not found.",
            reply_markup=get_back_keyboard(),
        )
        await callback_query.answer()
        return

    logging.info(f"Found appointment: {dict(appointment)}")

    # Store appointment info for confirmation
    await state.update_data(
        cancel_appt_id=appointment_id,
        cancel_service=appointment["service"],
        cancel_date=appointment["appointment_date"],
        cancel_time=appointment["time_slot"],
    )

    date_formatted = format_date(appointment["appointment_date"])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yes, cancel", callback_data=f"confirm_cancel_appt_{appointment_id}")],
            [InlineKeyboardButton(text="❌ No, keep it", callback_data="my_appointments")],
        ]
    )

    logging.info(f"Sending confirmation message with keyboard: {keyboard.inline_keyboard}")

    try:
        await callback_query.message.answer(
            f"Are you sure you want to cancel this appointment?\n\n"
            f"📌 <b>{appointment['service'].capitalize()}</b>\n"
            f"📅 Date: {date_formatted}\n"
            f"⏰ Time: {appointment['time_slot']}",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        logging.info("Confirmation message sent successfully")
    except Exception as e:
        logging.error(f"Failed to send confirmation: {e}")
        await callback_query.message.answer("Error showing confirmation. Please try again.")

    await callback_query.answer()


# Handle confirm cancel appointment
@dp.callback_query(lambda c: c.data.startswith("confirm_cancel_appt_"))
async def process_confirm_cancel_appt_callback(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    appointment_id = int(callback_query.data.replace("confirm_cancel_appt_", ""))

    logging.info(f"Confirm cancel: appt_id={appointment_id}, telegram_id={telegram_id}")

    # Cancel the appointment
    success = models.cancel_appointment_by_id(telegram_id, appointment_id)

    logging.info(f"Cancel result: success={success}")

    if success:
        # Get updated appointments list
        appointments = models.get_future_appointments(telegram_id)

        if not appointments:
            # No appointments left - show message and back button
            try:
                await callback_query.message.edit_text(
                    "✅ Your appointment has been cancelled.\n\n"
                    "You have no upcoming appointments.",
                    parse_mode="HTML",
                    reply_markup=get_back_keyboard(),
                )
            except Exception:
                # If edit fails, send new message
                await callback_query.message.answer(
                    "✅ Your appointment has been cancelled.\n\n"
                    "You have no upcoming appointments.",
                    parse_mode="HTML",
                    reply_markup=get_back_keyboard(),
                )
        else:
            # Show updated appointments list
            appointments_text = "📋 <b>Your upcoming appointments:</b>\n\n"

            for appt in appointments:
                date_formatted = format_date(appt["appointment_date"])
                appointments_text += (
                    f"📌 <b>{appt['service'].capitalize()}</b>\n"
                    f"📅 Date: {date_formatted}\n"
                    f"⏰ Time: {appt['time_slot']}\n"
                    f"👤 Name: {appt['name']}\n"
                    f"📞 Phone: {appt['phone']}\n\n"
                )

            try:
                await callback_query.message.edit_text(
                    appointments_text,
                    parse_mode="HTML",
                    reply_markup=get_appointments_keyboard(appointments),
                )
            except Exception:
                # If edit fails, send new message
                await callback_query.message.answer(
                    appointments_text,
                    parse_mode="HTML",
                    reply_markup=get_appointments_keyboard(appointments),
                )
    else:
        await callback_query.message.answer(
            "Failed to cancel appointment. Please try again.",
            reply_markup=get_back_keyboard(),
        )

    await state.clear()
    await callback_query.answer()


# Handle edit appointment from my appointments
@dp.callback_query(lambda c: c.data.startswith("edit_appt_"))
async def process_edit_appt_callback(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    appointment_id = int(callback_query.data.replace("edit_appt_", ""))

    # Get appointment details
    appointment = models.get_appointment_by_id(telegram_id, appointment_id)

    if not appointment:
        await callback_query.message.answer(
            "Appointment not found.",
            reply_markup=get_back_keyboard(),
        )
        await callback_query.answer()
        return

    # Store appointment info in state
    await state.update_data(
        edit_appt_id=appointment_id,
        edit_service=appointment["service"],
        edit_date=appointment["appointment_date"],
        edit_time=appointment["time_slot"],
        edit_name=appointment["name"],
        edit_phone=appointment["phone"],
    )

    # Show edit menu with all options
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📌 Change service", callback_data=f"edit_service_{appointment_id}")],
            [InlineKeyboardButton(text="📅 Change date", callback_data=f"edit_datetime_{appointment_id}")],
            [InlineKeyboardButton(text="👤 Change name", callback_data=f"edit_name_{appointment_id}")],
            [InlineKeyboardButton(text="📞 Change phone", callback_data=f"edit_phone_{appointment_id}")],
            [InlineKeyboardButton(text="⬅️ Back to appointments", callback_data="my_appointments")],
        ]
    )

    await callback_query.message.answer(
        "What would you like to change?",
        reply_markup=keyboard,
    )
    await callback_query.answer()
