from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

import os


load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))