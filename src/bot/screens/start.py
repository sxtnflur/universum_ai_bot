from aiogram.utils.i18n import gettext as _

from bot import keyboards
from bot.screens.base import ScreenDef
from config import settings


def first_start(start_balance: float):
    return ScreenDef(
        text=_(f'''
Привет! Я - бот для создания изображений в любой популярной нейросети

❗️ <b>Без обязательных подписок
❗️ Начального баланса хватает на любую модель
❗️ Самые низкие цены и пополнение баланса от 1 рубля</b>
        
Твой баланс: <b>{start_balance}</b> ⚡️

<b>Напиши какое фото создать:</b>
''')
    )


# def first_start(start_balance: float):
#     return ScreenDef(
#         text=f'''
# <b>Добро пожаловать в Universum AI 🚀</b>
#
# Здесь собраны мощные нейросети для:
# • генерации изображений
# • улучшения качества
# • редактирования и стилизации
#
# Всё в одном месте — просто и удобно.
#
# 🎁 На старте тебе начислено <b>{start_balance}</b> ⚡️, чтобы ты мог спокойно попробовать возможности бота.
#
# Выбирай модель для генерации здесь (нажми) 👉 /models'''
#     )


def menu(exchange_rate_rub: float = settings.EXCHANGE_RATE_RUB, exchange_rate_xtr: float = settings.EXCHANGE_RATE_XTR):
    return ScreenDef(
        text=_(f'<blockquote><b>Курс:</b>\n<b>1 ⚡️</b>= <b>1$</b> = <b>{exchange_rate_rub}₽</b> = '
               f'<b>{exchange_rate_xtr} ⭐ Telegram Stars</b></blockquote>\n\n'
               '<tg-emoji emoji-id="5348125953090403204">▶️</tg-emoji> '
               f'<a href="t.me/{settings.BOT_USERNAME}?start=command-models">'
               '<b>Выбрать модель для генерации</b></a>\n\n'
               '<tg-emoji emoji-id="5409048419211682843">💵</tg-emoji> '
               f'<a href="t.me/{settings.BOT_USERNAME}?start=command-balance"><b>Мой баланс</b></a>\n\n'
               f'<tg-emoji emoji-id="5397916757333654639">➕</tg-emoji> '
               f'<a href="t.me/{settings.BOT_USERNAME}?start=command-buy"><b>Пополнить баланс</b></a>\n\n'
               f'<tg-emoji emoji-id="5452069934089641166">❓</tg-emoji> '
               f'<a href="t.me/{settings.BOT_USERNAME}?start=command-support"><b>Поддержка</b></a>'),
        reply_markup=keyboards.menu.menu()
    )
