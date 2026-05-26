from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from bot import keyboards
from bot.keyboards.base import create_list_kb
from bot.keyboards.callback_datas.models import ScrollModelsCallback
from bot.keyboards.callback_datas.payment import SelectAmountUpBalanceCallback, SelectPaymentMethodCallback
from bot.screens.base import ScreenDef
from config import settings
from utils import price as price_utils
from utils.price import convert


def balance(balance: float):
    return ScreenDef(
        text=_(f'<tg-emoji emoji-id="5409048419211682843">💵</tg-emoji> '
               f'<b>Ваш баланс:</b> {balance} ⚡️\n\n'
               f'<a href="t.me/{settings.BOT_USERNAME}?start=command-buy">Пополнить баланс</a> | '
               f'<a href="t.me/{settings.BOT_USERNAME}?start=1">В меню</a>'),
    )


def main(
        exchange_rate_rub: float,
        exchange_rate_xtr: float
):
    ikb = create_list_kb(
        [1, 3, 5, 10, 100],
        get_btn=lambda p: InlineKeyboardButton(
            text=str(p), callback_data=SelectAmountUpBalanceCallback(amount=p).pack()
        ),
        width=5
    )
    ikb.append([
        InlineKeyboardButton(
            text=_('Указать свою сумму'), callback_data='balance-up-select-amount-myamount'
        )
    ])
    return ScreenDef(
        text=_('<tg-emoji emoji-id="5397916757333654639">➕</tg-emoji> <b>Выберите сумму пополнения баланса:</b>\n\n'
               f'<b>Курс:</b><blockquote>1 ⚡️= {exchange_rate_rub} руб\n\n'
               f'1 ⚡️= {exchange_rate_xtr} ⭐ Telegram Stars</blockquote>\n\n'
               f'<a href="t.me/{settings.BOT_USERNAME}?start=command-balance">Узнать мой баланс</a> | '
               f'<a href="t.me/{settings.BOT_USERNAME}?start=1">В меню</a>'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb)
    )


def payment_method(amount: float,
                   pay_username_url: str,
                   bot_username: str):
    return ScreenDef(
        text=_(f'<b>Сумма пополнения:</b> {amount} ⚡️\n\n<b>Выберите способ оплаты:</b>'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f'RUB [Карта/СБП] - {convert(amount, "rub")} руб',
                callback_data=SelectPaymentMethodCallback(
                    method='yookassa',
                    amount=amount
                ).pack()
            )],
            [InlineKeyboardButton(
                text=f'Telegram Stars - {convert(amount, "xtr")} ⭐',
                callback_data=SelectPaymentMethodCallback(
                    method='XTR',
                    amount=amount
                ).pack()
            )],
            [InlineKeyboardButton(
                text=_('Другой способ оплаты'),
                url=pay_username_url.replace('@', 'https://t.me/') + f'?text=Здравствуйте! Хочу купить {amount} ⚡️'
                                                                     f'в @{bot_username}'
                                                                     f'\nМне подошли данные способы оплаты'
            )],
            [InlineKeyboardButton(
                text=_('Назад'),
                callback_data='buy'
            )]
        ])
    )


def payment_link(link: str,
                 src_amount: float,
                 currency_amount: float,
                 currency_sign: str,
                 description: str,
                 support_url: str):
    return ScreenDef(
        text=_(f'<b>{description}</b>\n'
               f'При возникновении вопросов пишите сюда: {support_url}'),
        reply_markup=keyboards.payment.pay(
            src_amount=src_amount,
            currency_amount=currency_amount,
            currency_sign=currency_sign,
            link=link,
            telegram_pay_button=False
        )
    )


def on_payment(amount: float, balance: float):
    return ScreenDef(
        text=_(f'''
<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> Баланс успешно пополнен на {amount} ⚡️
<b>Текущий баланс: {balance}</b> ⚡️'''),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='К генерациям',
                callback_data=ScrollModelsCallback().pack()
            )]
        ])
    )
