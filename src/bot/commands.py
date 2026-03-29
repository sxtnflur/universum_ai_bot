import aiogram
from aiogram.types import BotCommand, BotCommandScopeDefault
from bot import menu

commands = [
    BotCommand(
        command='start',
        description='Перезапустить / Главное меню'
    ),
    BotCommand(
        command='models',
        description=menu.MODELS
    ),
    BotCommand(
        command='balance',
        description=menu.BALANCE
    ),
    BotCommand(
        command='buy',
        description=menu.BUY
    ),
    BotCommand(
        command='support',
        description=menu.SUPPORT
    )
]


async def set_my_commands(bot: aiogram.Bot):
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeDefault()
    )