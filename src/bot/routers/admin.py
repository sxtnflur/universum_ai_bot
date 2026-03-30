from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from bot.filters import IsAdmin
from config import settings
from db.decorator import db_connect
from db.repositories import UsersRepo
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
router.message.filter(IsAdmin(settings.ADMIN_IDS))
router.callback_query.filter(IsAdmin(settings.ADMIN_IDS))


@router.message(Command('admin'))
async def admin_menu(
    message: Message
):
    await message.answer(
        'balup 10 @username/user_id - Пополнить баланс'
    )


def get_user_filters(user: str):
    if user.isdigit():
        filters = dict(id=int(user))
    else:
        filters = dict(username=user.replace('@', ''))
    return filters


@router.message(F.text.startswith('balup '))
@db_connect()
async def up_balance(message: Message, *, db: AsyncSession):
    data = message.text.split()
    val, user = float(data[1]), data[2]
    upd_val = await UsersRepo(db).increase_field(
        filters=get_user_filters(user),
        field='balance',
        value=val
    )
    await message.answer(
        f'Баланс юзера {user} увеличен на {val}. Текущий баланс: {upd_val}'
    )


@router.message(F.text.startswith('baldown '))
@db_connect()
async def down_balance(message: Message, *, db: AsyncSession):
    data = message.text.split()
    val, user = float(data[1]), data[2]
    upd_val = await UsersRepo(db).decrease_field(
        filters=get_user_filters(user),
        field='balance',
        value=val
    )
    await message.answer(
        f'Баланс юзера {user} уменьшен на {val}. Текущий баланс: {upd_val}'
    )


@router.message(F.text.startswith('balshow '))
@db_connect()
async def show_balance(message: Message, *, db: AsyncSession):
    data = message.text.split()
    user = data[1]
    balance = await UsersRepo(db).get_one_field('balance', **get_user_filters(user))
    await message.answer(
        f'Баланс юзера {user} = {balance}'
    )