from config import settings
from typing_extensions import Literal


Currency = Literal['rub', 'xtr']


def process_amount(amount: float, min_val: float = 0.01, round_digits: int = 2):
    return max(round(amount * 1.5, round_digits), min_val)


def get_currency_by_method(method: Literal['yookassa', 'XTR']) -> Currency:
    return {
        'yookassa': 'rub',
        'XTR': 'xtr'
    }[method]


def get_convert_factor(currency: Currency):
    return {
        'xtr': settings.EXCHANGE_RATE_XTR,
        'rub': settings.EXCHANGE_RATE_RUB
    }[currency.lower()]


def convert(amount: float, to: Currency = 'xtr'):
    return amount * get_convert_factor(to)


def get_sign(currency: Currency):
    return {
        'xtr': '⭐',
        'rub': 'руб.'
    }[currency]


def get_min_amount(currency: Currency):
    return {
        'xtr': 1,
        'rub': 1
    }[currency]