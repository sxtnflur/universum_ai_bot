import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot.filters import IsAdmin
from config import settings
from db.decorator import db_connect
from db.repositories import UsersRepo, PaymentsRepo
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
router.message.filter(IsAdmin(settings.ADMIN_IDS))
router.callback_query.filter(IsAdmin(settings.ADMIN_IDS))


@router.message(Command('admin'))
async def admin_menu(
    message: Message
):
    await message.answer(
        'Пополнить баланс на 10: <code>balup</code> 10 @username/user_id\n'
        'Уменьшить баланс на 10: <code>baldown</code> 10 @username/user_id\n'
        'Посмотреть баланс: <code>balshow</code> 10 @username/user_id\n',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Статистика',
                callback_data='admin:stat'
            )]
        ])
    )


@router.callback_query(F.data == 'admin:stat')
@db_connect()
async def stat(call: CallbackQuery, *, db: AsyncSession):
    users_total = await UsersRepo(db).count()
    users_come_last24h = await UsersRepo(db).count(created_at__ge=datetime.datetime.utcnow()-datetime.timedelta(hours=24))
    users_come_last7d = await UsersRepo(db).count(created_at__ge=datetime.datetime.utcnow()-datetime.timedelta(days=7))

    payments_total = await PaymentsRepo(db).count()
    payments_last24h = await PaymentsRepo(db).count(created_at__ge=datetime.datetime.utcnow()-datetime.timedelta(hours=24))
    payments_last7d = await PaymentsRepo(db).count(created_at__ge=datetime.datetime.utcnow()-datetime.timedelta(days=7))

    payments_amount_total = await PaymentsRepo(db).sum('amount')
    payments_amount_last24h = await PaymentsRepo(db).sum(
        'amount',
        created_at__ge=datetime.datetime.utcnow() - datetime.timedelta(hours=24))
    payments_amount_last7d = await PaymentsRepo(db).sum(
        'amount',
        created_at__ge=datetime.datetime.utcnow() - datetime.timedelta(days=7))

    await call.message.answer(
        f'Всего пользователей: {users_total}\n'
        f'Пришло за последние 24ч: {users_come_last24h}\n'
        f'Пришло за последние 7 дней: {users_come_last7d}\n\n'
        f'Оплат всего: {payments_total} на сумму {payments_amount_total or 0}\n'
        f'Оплат за последние 24ч: {payments_last24h} на сумму {payments_amount_last24h or 0}\n'
        f'Оплат за последние 24ч: {payments_last7d} на сумму {payments_amount_last7d or 0}'
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