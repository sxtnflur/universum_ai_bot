from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import settings

router = Router()


@router.message(Command('support'))
async def support(
    message: Message
):
    await message.answer(f'Если у вас возникли вопросы, обращайтесь: {settings.SUPPORT_URL}')