from aiogram import types, F
from aiogram.fsm.context import FSMContext
from config import dp, format_date
from keyboards import (
    get_services_keyboard,
    get_back_keyboard,
    get_dates_keyboard,
    get_time_slots_keyboard,
    get_confirm_keyboard,
    get_cancel_appointment_keyboard,
    get_main_menu_keyboard,
    get_phone_keyboard,
)
from constants import (
    WELCOME_MESSAGE,
    SERVICE_SELECTED_TITLE,
    SERVICE_SELECTED_DESCRIPTION,
    ASK_NAME_MESSAGE,
    ASK_PHONE_MESSAGE,
    PHONE_FORMAT_ERROR,
    CONFIRMATION_WITH_CLIENT_INFO,
    EDIT_BOOKING_HINT,
    BOOKING_CONFIRMED_WITH_CLIENT,
)
from states import BookingState
import models


# Handle service button clicks - check for existing appointments or edit mode
@dp.callback_query(lambda c: c.data.startswith("service_"))
async def process_service_callback(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.replace("service_", "").capitalize()
    telegram_id = callback_query.from_user.id

    # Check if we're in editing mode from "My appointments"
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # We're editing an existing appointment - update the service immediately
        edit_service = service.lower()
        edit_date = data.get("edit_date")
        edit_time = data.get("edit_time")
        edit_name = data.get("edit_name")
        edit_phone = data.get("edit_phone")

        # Cancel old appointment and create new one
        models.cancel_appointment_by_id(telegram_id, edit_appt_id)
        models.create_appointment(
            telegram_id,
            edit_service,
            edit_date,
            edit_time,
            edit_name,
            edit_phone,
        )

        await callback_query.message.answer(
            f"📌 <b>{edit_service.capitalize()}</b>\n"
            f"📅 Date: {format_date(edit_date)}\n"
            f"⏰ Time: {edit_time}\n"
            f"👤 Name: {edit_name}\n"
            f"📞 Phone: {edit_phone}",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        await callback_query.answer()
        return

    # Check if user already has an appointment for this service
    existing = models.check_existing_appointment(telegram_id, service)

    if existing:
        # User already has appointment - offer to cancel
        appointment_date = existing["appointment_date"]
        time_slot = existing["time_slot"]
        formatted_date = format_date(appointment_date)

        await callback_query.message.answer(
            f"You already have an appointment for <b>{service}</b>:\n\n"
            f"📅 Date: {formatted_date}\n"
            f"⏰ Time: {time_slot}\n\n"
            f"Would you like to cancel this appointment and book a new one?",
            parse_mode="HTML",
            reply_markup=get_cancel_appointment_keyboard(service.lower()),
        )
        await callback_query.answer()
        return

    # No existing appointment - proceed with booking
    await state.update_data(service=service)
    await callback_query.message.answer(
        SERVICE_SELECTED_TITLE.format(service=service) + "\n\n"
        + SERVICE_SELECTED_DESCRIPTION + "\n\n"
        + "Please select a date for your appointment:",
        parse_mode="HTML",
        reply_markup=get_dates_keyboard(service.lower()),
    )
    await state.set_state(BookingState.selecting_date)
    await callback_query.answer()


# Handle "Yes, cancel my appointment" button (for duplicate service booking)
@dp.callback_query(lambda c: c.data.startswith("confirm_cancel_") and not c.data.startswith("confirm_cancel_appt_"))
async def confirm_cancel_appointment(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.replace("confirm_cancel_", "").capitalize()
    telegram_id = callback_query.from_user.id

    # Cancel the appointment
    models.cancel_appointment(telegram_id, service.lower())

    await state.update_data(service=service)
    await callback_query.message.answer(
        f"Your appointment for <b>{service}</b> has been cancelled.\n\n"
        f"Now please select a new date:",
        parse_mode="HTML",
        reply_markup=get_dates_keyboard(service.lower()),
    )
    await state.set_state(BookingState.selecting_date)
    await callback_query.answer()


# Handle "No, keep it" button
@dp.callback_query(lambda c: c.data.startswith("keep_appointment_"))
async def keep_appointment(callback_query: types.CallbackQuery):
    service = callback_query.data.replace("keep_appointment_", "").capitalize()

    await callback_query.message.answer(
        f"Your appointment for <b>{service}</b> has been kept.\n\n"
        f"Use the button below to return to services menu.",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(),
    )
    await callback_query.answer()


# Handle date selection (for booking or editing)
@dp.callback_query(lambda c: c.data.startswith("date_"))
async def process_date_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Check if it's editing mode callback: date_edit_{appt_id}_{date}
    if callback_query.data.startswith("date_edit_"):
        # Parse: date_edit_6_2026-03-14
        parts = callback_query.data.split("_", 3)
        appt_id = int(parts[2])
        date = parts[3]

        # Get service from state
        data = await state.get_data()
        edit_service = data.get("edit_service", "manicure")

        # Store new date and proceed to time selection
        await state.update_data(edit_date=date)
        await callback_query.message.answer(
            f"Selected date: <b>{format_date(date)}</b>\n\n"
            f"Please select a time slot:",
            parse_mode="HTML",
            reply_markup=get_time_slots_keyboard(edit_service, date),
        )
        await state.set_state(BookingState.selecting_time)
        await callback_query.answer()
        return

    # Regular booking callback: date_service_YYYY-MM-DD
    parts = callback_query.data.split("_", 2)
    service = parts[1]
    date = parts[2]

    # Check if we're in editing mode from "My appointments"
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # We're editing - store new date and proceed to time selection
        # Use edit_service from state, not service from callback (which is appt_id)
        edit_service = data.get("edit_service", service)
        await state.update_data(edit_date=date)
        await callback_query.message.answer(
            f"Selected date: <b>{format_date(date)}</b>\n\n"
            f"Please select a time slot:",
            parse_mode="HTML",
            reply_markup=get_time_slots_keyboard(edit_service, date),
        )
        await state.set_state(BookingState.selecting_time)
        await callback_query.answer()
        return

    # Regular booking flow
    await state.update_data(service=service, date=date)
    await callback_query.message.answer(
        f"Selected date: <b>{format_date(date)}</b>\n\n"
        f"Please select a time slot:",
        parse_mode="HTML",
        reply_markup=get_time_slots_keyboard(service, date),
    )
    await state.set_state(BookingState.selecting_time)
    await callback_query.answer()


# Handle time slot selection (for booking or editing)
@dp.callback_query(lambda c: c.data.startswith("time_"))
async def process_time_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Parse callback: time_service_YYYY-MM-DD_slot
    parts = callback_query.data.split("_", 3)
    service = parts[1]
    date = parts[2]
    time_slot = parts[3]

    # Check if we're in editing mode
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # We're editing - save all changes now (date + time + other fields)
        edit_service = data.get("edit_service")
        edit_name = data.get("edit_name")
        edit_phone = data.get("edit_phone")
        telegram_id = callback_query.from_user.id

        # Cancel old appointment and create new one
        models.cancel_appointment_by_id(telegram_id, edit_appt_id)
        models.create_appointment(
            telegram_id,
            edit_service,
            date,
            time_slot,
            edit_name,
            edit_phone,
        )

        await callback_query.message.answer(
            f"✅ Your appointment has been updated!\n\n"
            f"📌 <b>{edit_service.capitalize()}</b>\n"
            f"📅 Date: {format_date(date)}\n"
            f"⏰ Time: {time_slot}\n"
            f"👤 Name: {edit_name}\n"
            f"📞 Phone: {edit_phone}",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        await callback_query.answer()
        return

    # Regular booking flow
    await state.update_data(time_slot=time_slot)

    # Ask for name
    await callback_query.message.answer(
        ASK_NAME_MESSAGE,
        parse_mode="HTML",
    )
    await state.set_state(BookingState.entering_name)
    await callback_query.answer()


# Handle name input (for booking or editing)
@dp.message(BookingState.entering_name)
async def process_name_input(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if not name:
        await message.answer("Please enter a valid name:")
        return

    # Check if we're in editing mode
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # We're editing - update name and save changes immediately
        telegram_id = message.from_user.id
        edit_service = data.get("edit_service")
        edit_date = data.get("edit_date")
        edit_time = data.get("edit_time")
        edit_phone = data.get("edit_phone")

        # Cancel old appointment and create new one
        models.cancel_appointment_by_id(telegram_id, edit_appt_id)
        models.create_appointment(
            telegram_id,
            edit_service,
            edit_date,
            edit_time,
            name,
            edit_phone,
        )

        await message.answer(
            f"✅ Your appointment has been updated!\n\n"
            f"📌 <b>{edit_service.capitalize()}</b>\n"
            f"📅 Date: {format_date(edit_date)}\n"
            f"⏰ Time: {edit_time}\n"
            f"👤 Name: {name}\n"
            f"📞 Phone: {edit_phone}",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    # Regular booking flow
    await state.update_data(name=name)

    # Ask for phone
    await message.answer(
        ASK_PHONE_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_phone_keyboard(),
    )
    await state.set_state(BookingState.entering_phone)


# Handle phone input (text or contact) - for booking or editing
@dp.message(BookingState.entering_phone)
async def process_phone_input(message: types.Message, state: FSMContext):
    from config import validate_phone, format_phone
    import logging

    # Check if it's a contact
    if message.contact:
        logging.info(f"Received contact: {message.contact}")
        phone = message.contact.phone_number
        logging.info(f"Phone from contact: {phone}")
    else:
        phone = message.text.strip() if message.text else ""
        logging.info(f"Phone from text: {phone}")

    if not phone:
        await message.answer(
            PHONE_FORMAT_ERROR,
            parse_mode="HTML",
            reply_markup=get_phone_keyboard(),
        )
        return

    if not validate_phone(phone):
        await message.answer(
            PHONE_FORMAT_ERROR,
            parse_mode="HTML",
            reply_markup=get_phone_keyboard(),
        )
        return

    # Format phone to standard format
    formatted_phone = format_phone(phone)
    logging.info(f"Formatted phone: {formatted_phone}")

    # Check if we're in editing mode
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # We're editing - update phone and save changes to database
        await state.update_data(edit_phone=formatted_phone)

        # Get all edited data
        telegram_id = message.from_user.id
        edit_service = data.get("edit_service")
        edit_date = data.get("edit_date")
        edit_time = data.get("edit_time")
        edit_name = data.get("edit_name")
        edit_phone = formatted_phone

        # Cancel old appointment and create new one
        models.cancel_appointment_by_id(telegram_id, edit_appt_id)
        models.create_appointment(
            telegram_id,
            edit_service,
            edit_date,
            edit_time,
            edit_name,
            edit_phone,
        )

        await message.answer(
            f"✅ Your appointment has been updated!\n\n"
            f"📌 <b>{edit_service.capitalize()}</b>\n"
            f"📅 Date: {format_date(edit_date)}\n"
            f"⏰ Time: {edit_time}\n"
            f"👤 Name: {edit_name}\n"
            f"📞 Phone: {edit_phone}",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    # Regular booking flow
    await state.update_data(phone=formatted_phone)

    # Get all data for confirmation
    data = await state.get_data()
    logging.info(f"State data: {data}")

    service = data["service"]
    date = format_date(data["date"])
    time_slot = data["time_slot"]
    name = data["name"]
    phone = formatted_phone

    # Show confirmation with empty keyboard
    await message.answer(
        CONFIRMATION_WITH_CLIENT_INFO.format(
            service=service,
            date=date,
            time_slot=time_slot,
            name=name,
            phone=phone,
        ) + "\n\n" + EDIT_BOOKING_HINT,
        parse_mode="HTML",
        reply_markup=get_confirm_keyboard(service.lower(), data["date"], time_slot),
    )
    await state.set_state(BookingState.confirming)


# Handle confirmation (but not confirm_cancel_appt_ which is for my appointments)
@dp.callback_query(lambda c: c.data.startswith("confirm_") and not c.data.startswith("confirm_cancel_"))
async def process_confirm_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Parse callback: confirm_service_YYYY-MM-DD_slot
    parts = callback_query.data.split("_", 3)
    service = parts[1]
    date = parts[2]
    time_slot = parts[3]

    telegram_id = callback_query.from_user.id

    # Get client info from state
    data = await state.get_data()
    name = data.get("name", "N/A")
    phone = data.get("phone", "N/A")

    # Create appointment in database
    success, appointment_id = models.create_appointment(telegram_id, service, date, time_slot, name, phone)

    if success:
        # Save appointment_id for review request
        await state.update_data(appointment_id=appointment_id)
        
        await callback_query.message.answer(
            BOOKING_CONFIRMED_WITH_CLIENT.format(
                service=service.capitalize(),
                date=format_date(date),
                time_slot=time_slot,
                name=name,
                phone=phone,
            ),
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
    else:
        await callback_query.message.answer(
            f"Sorry, this time slot is no longer available.\n"
            f"Please choose another time.",
            reply_markup=get_time_slots_keyboard(service, date),
        )

    await state.clear()
    await callback_query.answer()
