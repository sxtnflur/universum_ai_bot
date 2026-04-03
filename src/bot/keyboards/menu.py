from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.menu import MODELS, SUPPORT, BALANCE, BUY


def menu():
    return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=MODELS),
             KeyboardButton(text=SUPPORT)],
            [KeyboardButton(text=BALANCE),
             KeyboardButton(text=BUY)]
        ],
            resize_keyboard=True,
        )