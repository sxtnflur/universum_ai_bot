from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from config import settings
from bot.menu import SUPPORT

router = Router()


@router.message(Command('support'))
@router.message(F.text == SUPPORT)
async def support(
    message: Message
):
    await message.answer(f'Если у вас возникли вопросы, обращайтесь: {settings.SUPPORT_URL}')