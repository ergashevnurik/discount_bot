from aiogram.dispatcher.filters.state import *


class BotState(StatesGroup):
    # chooseLanguage = State()
    contact = State()
    firstName = State()
    lastName = State()
    birthday = State()
    gender = State()

