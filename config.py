from aiogram import *
from aiogram.contrib.fsm_storage.memory import *
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import *
from aiogram.contrib.middlewares.i18n import I18nMiddleware

TOKEN = "1050386123:AAEz23KQ8E9RB7fHDN6XuwNw88CcENqK0MQ"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


I18N_DOMAIN = 'testbot'

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

# Setup i18n middleware
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

# Alias for gettext method
_ = i18n.gettext

ADMINS = [972931399]