from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import menu
from bot.commands import commands


from .start import start
from .support import support
from .payment import buy, balance
from .models import models_list_m

router = Router()


@router.message(Command(commands=(command.command for command in commands)))
async def all_menu_commands(
    message: Message,
    state: FSMContext,
    command: CommandObject | None = None
):
    await state.clear()
    if command.command == 'start':
        return await start(message, command, state)
    if command.command == 'models':
        return await models_list_m(message)
    if command.command == 'support':
        return await support(message)
    if command.command == 'buy':
        return await buy(message, state)
    if command.command == 'balance':
        return await balance(message)


@router.message(F.text.in_((menu.MODELS, menu.BUY, menu.SUPPORT, menu.BALANCE)))
async def all_menu_buttons(
    message: Message,
    state: FSMContext
):
    await state.clear()
    if message.text == menu.MODELS:
        return await models_list_m(message)
    if message.text == menu.SUPPORT:
        return await support(message)
    if message.text == menu.BUY:
        return await buy(message, state)
    if message.text == menu.BALANCE:
        return await balance(message)
