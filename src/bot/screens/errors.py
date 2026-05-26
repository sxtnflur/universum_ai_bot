from bot.screens.base import ScreenDef


def not_number_sent():
    return ScreenDef(
        text='Можно ввести только число'
    )


def not_int_send():
    return ScreenDef(
        text='Можно ввести только целое число'
    )


def too_little_number(min: int):
    return ScreenDef(
        text=f'Минимальное значение: {min}'
    )


def too_big_number(max: int):
    return ScreenDef(
        text=f'Максимально значение: {max}'
    )


def prompt_not_sent():
    return ScreenDef(
        text='Отправьте ваш промпт:'
    )


def image_not_send():
    return ScreenDef(
        text='Отправьте изображения:'
    )