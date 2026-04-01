import loggers
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from config import settings
from db.decorator import db_connect
from db.repositories import UsersRepo
from depends import payment_factory, payment_service
from sqlalchemy.ext.asyncio import AsyncSession
from utils import price as price_util

from .. import screens, keyboards
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
    currency = price_util.get_currency_by_method(callback_data.method)

    min_amount = price_util.get_min_amount(currency)
    if callback_data.amount < min_amount:
        await call.answer(f'Минимальная сумма пополнения ДЛЯ ЭТОГО МЕТОДА оплаты равна {min_amount}\n',
                          show_alert=True)
        return

    amount = round(price_util.convert(amount=callback_data.amount, to=currency), 2)
    currency_sign = price_util.get_sign(currency)

    if callback_data.method == 'XTR':
        try:
            amount = int(amount)
        except ValueError:
            await call.answer(
                'Для ЭТОГО МЕТОДА оплаты сумма пополнения должна быть кратна 200 (200/250/300/350 и т.д)'
            )
            return

        description = f'Пополнение баланса на {callback_data.amount} ⚡️'

        await call.bot.send_invoice(
            chat_id=call.message.chat.id,
            title=description,
            currency='XTR',
            description=f'При возникновении вопросов пишите сюда: {settings.SUPPORT_URL}',
            payload=f'upbalance:xtr:{amount}',
            prices=[LabeledPrice(label=description, amount=amount)],
            provider_token='',
            reply_markup=keyboards.payment.pay(
                src_amount=callback_data.amount,
                currency_amount=amount,
                currency_sign=currency_sign,
                telegram_pay_button=True
            )
        )
        return
    else:
        description = f'Пополнение баланса на {callback_data.amount} ⚡️'

        pay = await payment_factory.create_payment(
            amount=callback_data.amount,
            description=description,
            payment_method=callback_data.method,
            session=await call.bot.session.create_session(),
            metadata=dict(user_id=call.from_user.id)
        )
        pay_link = pay.url
        await screens.payment.payment_link(
            link=pay_link,
            src_amount=callback_data.amount,
            currency_amount=amount,
            currency_sign=currency_sign,
            description=description,
            support_url=settings.SUPPORT_URL
        ).answer(call, 'edit')


@router.pre_checkout_query()
async def pre_check(pre_checkout_query: PreCheckoutQuery):
    try:
        currency = pre_checkout_query.currency.lower()
        factor = price_util.get_convert_factor(currency)
        amount = round(pre_checkout_query.total_amount / factor, 2)
    except Exception as e:
        await pre_checkout_query.answer(ok=False, error_message=str(e))
        loggers.payment.error('Ошибка при pre_checkout_query', exc_info=True)
        return

    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def get_telegram_payment(message: Message):
    try:
        currency = message.successful_payment.currency.lower()
        factor = price_util.get_convert_factor(currency)
        amount = round(message.successful_payment.total_amount / factor, 2)
        await payment_service.on_payment(
            user_id=message.from_user.id,
            amount=amount,
            method='XTR',
            order_id=message.successful_payment.telegram_payment_charge_id
        )
    except:
        loggers.payment.error('Ошибка при pre_checkout_query', exc_info=True)