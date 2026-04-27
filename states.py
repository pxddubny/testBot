from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    choosing_date = State()
    choosing_time = State()
    waiting_name = State()
    waiting_phone = State()
    confirming = State()


class AdminStates(StatesGroup):
    add_day = State()
    add_slot_date = State()
    add_slot_time = State()
    delete_slot_date = State()
    delete_slot_time = State()
    close_day = State()
    view_schedule_date = State()
    cancel_client_date = State()
    cancel_client_time = State()
