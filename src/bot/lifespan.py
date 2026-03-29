from aiogram.types import BotCommand, BotCommandScopeDefault
from . import menu
from .commands import set_my_commands
from .loader import bot


async def onstartup(*args, **kwargs):
    await set_my_commands(bot=bot)