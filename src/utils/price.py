from typing_extensions import Literal


Currency = Literal['rub', 'xtr']


def process_amount(amount: float):
    return round(amount * 100, 2)


def get_currency_by_method(method: Literal['yookassa', 'XTR']) -> Currency:
    return {
        'yookassa': 'rub',
        'XTR': 'xtr'
    }[method]


def get_convert_factor(currency: Currency):
    return {
        'xtr': 0.02,
        'rub': 1
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
        'xtr': 200,
        'rub': 1
    }[currency]