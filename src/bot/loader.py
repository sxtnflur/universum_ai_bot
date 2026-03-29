from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import settings

bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(
              parse_mode=ParseMode.HTML,
              link_preview_is_disabled=True
          ))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)