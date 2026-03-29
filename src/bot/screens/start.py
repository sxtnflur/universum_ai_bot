from bot.screens.base import ScreenDef


def menu():
    return ScreenDef(
        text='''
<tg-emoji emoji-id="5348125953090403204">▶️</tg-emoji> <b>Выбрать модель для генерации:</b> /models

<tg-emoji emoji-id="5409048419211682843">💵</tg-emoji> <b>Мой баланс:</b> /balance

<tg-emoji emoji-id="5397916757333654639">➕</tg-emoji> <b>Пополнить баланс:</b> /buy

<tg-emoji emoji-id="5452069934089641166">❓</tg-emoji> <b>Поддержка:</b> /support
'''
    )