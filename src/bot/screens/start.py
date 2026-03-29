from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.screens.base import ScreenDef
from bot.menu import MODELS, BALANCE, BUY, SUPPORT


def first_start(start_balance: float):
    return ScreenDef(
        text=f'''
<b>Добро пожаловать в Universum AI 🚀</b>

Здесь собраны мощные нейросети для:
• генерации изображений  
• улучшения качества  
• редактирования и стилизации  

Всё в одном месте — просто и удобно.

🎁 На старте тебе начислено <b>{start_balance}</b> ⚡️, чтобы ты мог спокойно попробовать возможности бота.

Выбирай модель для генерации здесь (нажми) 👉 /models'''
    )


def menu():
    return ScreenDef(
        text='''
<tg-emoji emoji-id="5348125953090403204">▶️</tg-emoji> <b>Выбрать модель для генерации:</b> /models

<tg-emoji emoji-id="5409048419211682843">💵</tg-emoji> <b>Мой баланс:</b> /balance

<tg-emoji emoji-id="5397916757333654639">➕</tg-emoji> <b>Пополнить баланс:</b> /buy

<tg-emoji emoji-id="5452069934089641166">❓</tg-emoji> <b>Поддержка:</b> /support
''',
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=MODELS),
             KeyboardButton(text=SUPPORT)],
            [KeyboardButton(text=BALANCE),
             KeyboardButton(text=BUY)]
        ],
            resize_keyboard=True,
        )
    )
