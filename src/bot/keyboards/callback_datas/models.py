from aiogram.filters.callback_data import CallbackData
from mytypes import ActionType
from .base import ScrollingCallback


class SelectModelCallback(CallbackData, prefix='select-model'):
    key: str
    action_type: str | None = None


class ScrollModelsCallback(ScrollingCallback, prefix='scroll-models'):
    ...


class SelectRatioCallback(CallbackData, prefix='select-ratio'):
    ratio: str


class SelectResolutionCallback(CallbackData, prefix='select-resolution'):
    resolution: str


class SelectNumImagesCallback(CallbackData, prefix='select-num_images'):
    num_images: int


class SelectInputNumberParamCallback(CallbackData, prefix='select-input-num'):
    param: str