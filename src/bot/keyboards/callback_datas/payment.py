from aiogram.filters.callback_data import CallbackData


class SelectAmountUpBalanceCallback(CallbackData, prefix='balance-up-select-amount'):
    amount: float


class SelectPaymentMethodCallback(CallbackData, prefix='select-pay-method'):
    method: str
    amount: float