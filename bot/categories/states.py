from aiogram.fsm.state import StatesGroup, State


class CategoryStates(StatesGroup):
    entering_name = State()
    entering_emoji = State()
    renaming = State()
