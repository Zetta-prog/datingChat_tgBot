from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    name = State()
    age = State()

class Dialogue(StatesGroup):
    search = State()
    found = State()

class EditForm(StatesGroup):
    name = State()
    age = State()
