from aiogram.types import BotCommand, BotCommandScopeDefault
from .loader import bot


async def onstartup(*args, **kwargs):
    await bot.set_my_commands(
        commands=[
            BotCommand(
                command='start',
                description='Перезапустить / Главное меню'
            ),
            BotCommand(
                command='models',
                description='Выбрать модель для генерации'
            ),
            BotCommand(
                command='balance',
                description='Мой баланс'
            ),
            BotCommand(
                command='buy',
                description='Пополнить баланс'
            ),
            BotCommand(
                command='support',
                description='Поддержка'
            )
        ],
        scope=BotCommandScopeDefault()
    )