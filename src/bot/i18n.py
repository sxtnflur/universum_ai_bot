from aiogram.utils.i18n import I18n
from config import settings

i18n = I18n(path=f"{settings.BASE_SRC}locales", default_locale="en", domain="messages")