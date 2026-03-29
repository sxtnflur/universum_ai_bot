from aiogram.filters.callback_data import CallbackData


class ScrollingCallback(CallbackData, prefix='scrolling'):
    page: int = 0
    limit: int = 10


# class GoToStartScreenDefCallback(CallbackData, prefix='go-to-screen'):
#     num: int
#