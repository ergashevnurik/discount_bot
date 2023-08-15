from aiogram.types import *
from strings import *
from config import _

choose_language = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(_("🇷🇺Русский язык"))).add(KeyboardButton(_("🇺🇿O'zbek tili")))
send_contact = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(_("📩 Отправить"), request_contact=True))

gender_btn = ReplyKeyboardMarkup(resize_keyboard=True, selective=True).row(KeyboardButton(male), KeyboardButton(female)).add(KeyboardButton(other))

menu = ReplyKeyboardMarkup(resize_keyboard=True)\
    .row(KeyboardButton(_("🛒 Мои покупки")), KeyboardButton(_("👑 Программа лояльности")))\
    .row(KeyboardButton(_("💳 Моя карта")), KeyboardButton(_("🔶 Ваш профиль"))).add(KeyboardButton(_("➕ Подключить карту")))

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)\
    .row(KeyboardButton(_("🛒 Мои покупки")), KeyboardButton(_("👑 Программа лояльности")))\
    .row(KeyboardButton(_("💳 Моя карта")), KeyboardButton(_("🔶 Ваш профиль"))).row(KeyboardButton(_('📃 Список пользователей')), KeyboardButton(_('➕ Подключить карту')))
