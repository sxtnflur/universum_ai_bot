from aiogram.filters.callback_data import CallbackData


class SelectAmountUpBalanceCallback(CallbackData, prefix='balance-up-select-amount'):
    amount: float