from aiogram.dispatcher.filters.state import *


class BotState(StatesGroup):
    # chooseLanguage = State()
    contact = State()
    firstName = State()
    lastName = State()
    birthday = State()
    gender = State()


class ConnectCardState(StatesGroup):
    cardNumber = State()
    cardDate = State()
    cardName = State()
