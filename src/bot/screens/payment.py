from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.base import create_list_kb
from bot.keyboards.callback_datas.models import ScrollModelsCallback
from bot.keyboards.callback_datas.payment import SelectAmountUpBalanceCallback, SelectPaymentMethodCallback
from bot.screens.base import ScreenDef


def balance(balance: float):
    return ScreenDef(
        text=f'<tg-emoji emoji-id="5409048419211682843">💵</tg-emoji> '
             f'<b>Ваш баланс:</b> {balance} ⚡️\n<blockquote>Пополнить баланс: /buy\nВ меню: /start</blockquote>',
    )


def main():
    ikb = create_list_kb(
        [100, 500, 1000, 5000],
        get_btn=lambda p: InlineKeyboardButton(
            text=str(p), callback_data=SelectAmountUpBalanceCallback(amount=p).pack()
        ),
        width=4
    )
    ikb.append([
        InlineKeyboardButton(
            text='Указать свою сумму', callback_data='balance-up-select-amount-myamount'
        )
    ])
    return ScreenDef(
        text='<tg-emoji emoji-id="5397916757333654639">➕</tg-emoji> <b>Выберите сумму пополнения баланса:</b>\n'
             '1 руб = 1 ⚡️'
             '\n<blockquote>Узнать мой баланс: /balance\nВ меню: /start</blockquote>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb)
    )


def payment_method(amount: float,
                   pay_username_url: str):
    return ScreenDef(
        text=f'<b>Сумма пополнения:</b> {amount} ⚡️\n\n<b>Выберите способ оплаты:</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='ЮКасса (Временно недоступно)',
                callback_data=SelectPaymentMethodCallback(
                    method='yookassa',
                    amount=amount
                ).pack()
            )],
            [InlineKeyboardButton(
                text='Через поддержку',
                url=pay_username_url
            )],
            [InlineKeyboardButton(
                text='Назад',
                callback_data='buy'
            )]
        ])
    )


def payment_link(link: str, amount: float):
    return ScreenDef(
        text=f'Для пополнения баланса на сумму: {amount} руб. перейдите по кнопке "Пополнить" и совершите оплату:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Пополнить',
                url=link
            )],
            [InlineKeyboardButton(
                text='Назад',
                callback_data=SelectAmountUpBalanceCallback(amount=amount).pack()
            )]
        ])
    )


def on_payment(amount: float, balance: float):
    return ScreenDef(
        text=f'''
<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> Баланс успешно пополнен на {amount} ⚡️
<b>Текущий баланс: {balance}</b> ⚡️''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='К генерациям',
                callback_data=ScrollModelsCallback().pack()
            )]
        ])
    )