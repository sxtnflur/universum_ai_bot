from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from config import settings
from db.decorator import db_connect
from db.repositories import UsersRepo
from depends import payment_factory
from sqlalchemy.ext.asyncio import AsyncSession

from .. import screens
from ..keyboards.callback_datas.payment import SelectAmountUpBalanceCallback, SelectPaymentMethodCallback
from bot.menu import BALANCE, BUY

router = Router()


class BuyStates(StatesGroup):
    amount = State()


@router.message(Command('balance'))
@router.message(F.text == BALANCE)
@db_connect()
async def balance(message: Message, *, db: AsyncSession):
    bal = await UsersRepo(db).get_one_field('balance', id=message.from_user.id)
    await screens.payment.balance(balance=bal).answer(message)


@router.message(Command('buy'))
@router.message(F.text == BUY)
async def buy(message: Message, state: FSMContext):
    await screens.payment.main().answer(message)
    await state.set_state(BuyStates.amount)


@router.callback_query(F.data == 'buy')
async def buy_call(call: CallbackQuery, state: FSMContext):
    await screens.payment.main().answer(call, 'edit')
    await state.set_state(BuyStates.amount)


@router.callback_query(SelectAmountUpBalanceCallback.filter())
async def select_amount(
    call: CallbackQuery, callback_data: SelectAmountUpBalanceCallback
):
    await screens.payment.payment_method(callback_data.amount, settings.SUPPORT_URL).answer(call, 'edit')


@router.callback_query(F.data == 'balance-up-select-amount-myamount')
async def select_my_amount(
    call: CallbackQuery
):
    await call.message.answer('Введите сумму для пополнения:')


@router.message(BuyStates.amount)
async def input_amount(
    message: Message, state: State
):
    try:
        amount = float(message.text)
    except:
        await message.answer('Введите сумму пополнения (число)\n\nВ меню - /start')
        return

    if amount < settings.MIN_AMOUNT_UP_BALANCE:
        await message.answer(f'<b>Минимальная сумма пополнения:</b> {settings.MIN_AMOUNT_UP_BALANCE}')
        return

    await screens.payment.payment_method(amount, settings.SUPPORT_URL).answer(message)


@router.callback_query(SelectPaymentMethodCallback.filter())
async def select_pay_method(
    call: CallbackQuery,
    callback_data: SelectPaymentMethodCallback
):
    pay = await payment_factory.create_payment(
        amount=callback_data.amount,
        description=f'Пополнение баланса на {callback_data.amount}',
        payment_method=callback_data.method,
        session=await call.bot.session.create_session()
    )
    await screens.payment.payment_link(pay.url, amount=callback_data.amount).answer(call, 'edit')