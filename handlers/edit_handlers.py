from aiogram import types
from aiogram.fsm.context import FSMContext
from config import dp, format_date
from keyboards import (
    get_services_keyboard,
    get_back_keyboard,
    get_dates_keyboard,
    get_edit_booking_keyboard,
    get_confirm_keyboard,
    get_phone_keyboard,
    get_main_menu_keyboard,
)
from constants import (
    ASK_NAME_MESSAGE,
    ASK_PHONE_MESSAGE,
    CONFIRMATION_WITH_CLIENT_INFO,
    EDIT_BOOKING_HINT,
)
from states import BookingState
import models


# Handle edit booking button
@dp.callback_query(lambda c: c.data.startswith("edit_booking_"))
async def process_edit_booking_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Parse callback: edit_booking_service_YYYY-MM-DD_slot
    parts = callback_query.data.split("_", 3)
    service = parts[1]
    date = parts[2]
    time_slot = parts[3]

    await callback_query.message.answer(
        "What would you like to change?",
        reply_markup=get_edit_booking_keyboard(service, date, time_slot),
    )
    await callback_query.answer()


# Handle change service (from booking confirmation or my appointments)
@dp.callback_query(lambda c: c.data.startswith("edit_service_"))
async def process_edit_service_callback(callback_query: types.CallbackQuery, state: FSMContext):
    parts = callback_query.data.split("_", 3)

    # Check if it's from my appointments (edit_service_ID) or from booking (edit_service_service_date_slot)
    if len(parts) == 2:
        # From my appointments: edit_service_ID - show services keyboard with edit mode callback
        await callback_query.message.answer(
            "Please select a new service:",
            reply_markup=get_services_keyboard(),
        )
        await callback_query.answer()
        return

    # From booking confirmation: edit_service_service_YYYY-MM-DD_slot
    date = parts[2]
    time_slot = parts[3]

    await callback_query.message.answer(
        "Please select a new service:",
        reply_markup=get_services_keyboard(),
    )
    await state.set_state(BookingState.selecting_service)
    await callback_query.answer()


# Handle change date/time (from booking confirmation or my appointments)
@dp.callback_query(lambda c: c.data.startswith("edit_datetime_"))
async def process_edit_datetime_callback(callback_query: types.CallbackQuery, state: FSMContext):
    parts = callback_query.data.split("_", 3)

    # Check if it's from my appointments (edit_datetime_ID) or from booking (edit_datetime_service_date_slot)
    if len(parts) == 2:
        # From my appointments: edit_datetime_ID
        # Get service from state to show dates keyboard
        data = await state.get_data()
        service = data.get("edit_service", "manicure")
        appt_id = data.get("edit_appt_id")

        await callback_query.message.answer(
            "Please select a new date:",
            reply_markup=get_dates_keyboard(service, for_edit=True, appt_id=appt_id),
        )
        await callback_query.answer()
        return

    # From booking confirmation: edit_datetime_service_YYYY-MM-DD_slot
    service = parts[1]

    await callback_query.message.answer(
        "Please select a new date:",
        reply_markup=get_dates_keyboard(service),
    )
    await state.set_state(BookingState.selecting_date)
    await callback_query.answer()


# Handle change name (from booking confirmation or my appointments)
@dp.callback_query(lambda c: c.data.startswith("edit_name_"))
async def process_edit_name_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Check if we're in editing mode from my appointments
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # From my appointments - ask for new name
        await callback_query.message.answer(
            "Please enter your name:",
            parse_mode="HTML",
        )
        await state.set_state(BookingState.entering_name)
        await callback_query.answer()
        return

    # From booking confirmation
    await callback_query.message.answer(ASK_NAME_MESSAGE)
    await state.set_state(BookingState.entering_name)
    await callback_query.answer()


# Handle change phone (from booking confirmation or my appointments)
@dp.callback_query(lambda c: c.data.startswith("edit_phone_"))
async def process_edit_phone_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Check if we're in editing mode from my appointments
    data = await state.get_data()
    edit_appt_id = data.get("edit_appt_id")

    if edit_appt_id:
        # From my appointments - ask for new phone
        await callback_query.message.answer(
            ASK_PHONE_MESSAGE,
            parse_mode="HTML",
            reply_markup=get_phone_keyboard(),
        )
        await state.set_state(BookingState.entering_phone)
        await callback_query.answer()
        return

    # From booking confirmation
    await callback_query.message.answer(
        ASK_PHONE_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_phone_keyboard(),
    )
    await state.set_state(BookingState.entering_phone)
    await callback_query.answer()


# Handle back to confirmation
@dp.callback_query(lambda c: c.data.startswith("back_to_confirm_"))
async def process_back_to_confirm_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # Parse callback: back_to_confirm_service_YYYY-MM-DD_slot
    parts = callback_query.data.split("_", 4)
    service = parts[1]
    date = parts[2]
    time_slot = parts[3]

    # Get client info from state
    data = await state.get_data()
    name = data.get("name", "N/A")
    phone = data.get("phone", "N/A")

    await callback_query.message.answer(
        CONFIRMATION_WITH_CLIENT_INFO.format(
            service=service.capitalize(),
            date=format_date(date),
            time_slot=time_slot,
            name=name,
            phone=phone,
        ) + "\n\n" + EDIT_BOOKING_HINT,
        parse_mode="HTML",
        reply_markup=get_confirm_keyboard(service, date, time_slot),
    )
    await state.set_state(BookingState.confirming)
    await callback_query.answer()


# Handle cancel booking (but NOT cancel_appt_ which is for my appointments)
@dp.callback_query(lambda c: c.data.startswith("cancel_") and not c.data.startswith("cancel_appt_"))
async def process_cancel_callback(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.replace("cancel_", "").capitalize()

    await callback_query.message.answer(
        f"Booking cancelled.\n\n"
        f"Use the button below to return to services menu.",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(),
    )

    await state.clear()
    await callback_query.answer()
