from aiogram.types import *
from strings import *

choose_language = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(ru)).add(KeyboardButton(uz))
send_contact = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(f'📞 {send}', request_contact=True))

gender_btn = ReplyKeyboardMarkup(resize_keyboard=True, selective=True).row(KeyboardButton(male), KeyboardButton(female)).add(KeyboardButton(other))