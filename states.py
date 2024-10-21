from aiogram.fsm.state import State, StatesGroup

class PlayerCreation(StatesGroup):
    phase_01 = State()
    phase_02 = State()