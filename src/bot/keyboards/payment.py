from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.callback_datas.payment import SelectAmountUpBalanceCallback


def pay(
    src_amount: float,
    currency_amount: float,
    currency_sign: str,
    link: str | None = None,
    telegram_pay_button: bool = False
):
    return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f'Пополнить на {src_amount} ⚡️ за {currency_amount} {currency_sign}',
                url=link if not telegram_pay_button else None,
                pay=telegram_pay_button
            )],
            [InlineKeyboardButton(
                text='Назад',
                callback_data=SelectAmountUpBalanceCallback(amount=src_amount).pack()
            )]
        ])