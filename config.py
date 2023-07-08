from aiogram import *
from aiogram.contrib.fsm_storage.memory import *

TOKEN = "6091333849:AAE6Vao-3mIFVDLcA16ehTkHRQgaEY5NiCc"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

