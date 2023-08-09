from aiogram import *
from aiogram.contrib.fsm_storage.memory import *

TOKEN = "5952448521:AAEKbvVJuPsvj_WJ1-L4YZ6eMCoX3d9-I3g"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ADMINS = [972931399]