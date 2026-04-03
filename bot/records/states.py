from aiogram.fsm.state import StatesGroup, State


class RecordStates(StatesGroup):
    entering_text = State()
    editing_text = State()
