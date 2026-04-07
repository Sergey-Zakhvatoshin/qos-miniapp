from aiogram.fsm.state import State, StatesGroup


class BookingState(StatesGroup):
    selecting_service = State()
    selecting_date = State()
    selecting_time = State()
    entering_name = State()
    entering_phone = State()
    confirming = State()
    editing = State()


class ReviewState(StatesGroup):
    waiting_for_rating = State()
    waiting_for_review_text = State()
