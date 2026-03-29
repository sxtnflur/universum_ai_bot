from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import screens

router = Router()


@router.message()
async def unhandled_message(
    message: Message, state: FSMContext
):
    await state.clear()
    await screens.start.menu().answer(message)