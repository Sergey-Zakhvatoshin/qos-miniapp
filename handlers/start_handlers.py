from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import dp, bot
from keyboards import get_services_keyboard, get_useful_info_keyboard
from constants import WELCOME_MESSAGE, USEFUL_INFO_BUTTON
import models


# Handle /start command - sends welcome message to the user
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    # Create or update user in database
    models.create_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    await message.answer(
        WELCOME_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_services_keyboard(),
    )


# Handle "Useful information" button
@dp.callback_query(F.data == "useful_info")
async def show_useful_info(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="Here you can find useful information about our salon",
        reply_markup=get_useful_info_keyboard(),
    )


# Handle "Back to services" button
@dp.callback_query(F.data == "back_to_services")
async def back_to_services(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text=WELCOME_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_services_keyboard(),
    )
