from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from support import SUPPORT_TOKEN

bot = Bot(token=SUPPORT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)