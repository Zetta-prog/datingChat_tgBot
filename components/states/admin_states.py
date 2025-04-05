from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    mail_text = State()