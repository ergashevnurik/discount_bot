from aiogram import *
from aiogram.contrib.fsm_storage.memory import *

TOKEN = "6092971916:AAHDcmiEBR_49glpteQgI73EKt_fOcHVMsI"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

