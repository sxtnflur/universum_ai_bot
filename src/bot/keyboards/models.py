from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.keyboards.base import create_scrolling_kb, create_list_kb
from .callback_datas.models import SelectModelCallback, ScrollModelsCallback, SelectRatioCallback, \
    SelectResolutionCallback, SelectNumImagesCallback
from data import Model


def models_list(
    page: int,
    limit: int,
    models: list[Model]
):
    return create_scrolling_kb(
        page=page, limit=limit,
        objs=models,
        callback_data=ScrollModelsCallback,
        get_btn=lambda model: InlineKeyboardButton(
            text=model.title, callback_data=SelectModelCallback(key=model.key).pack()
        )
    )


def select_ratio(values: Iterable[str], current_value: str):
    ikb = [[InlineKeyboardButton(
        text=f'Оставить {current_value}',
        callback_data=SelectRatioCallback(ratio=current_value.replace(':', '-')).pack()
    )]]
    ikb.extend(create_list_kb(
        values, get_btn=lambda val: InlineKeyboardButton(
            text=val, callback_data=SelectRatioCallback(ratio=val.replace(':', '-')).pack()
        ), width=4
    ))
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def select_resolution(values: Iterable[str], current_value: str):
    ikb = [[InlineKeyboardButton(
        text=f'Оставить {current_value}',
        callback_data=SelectResolutionCallback(resolution=current_value).pack()
    )]]
    ikb.extend(create_list_kb(
        values, get_btn=lambda val: InlineKeyboardButton(
            text=val, callback_data=SelectResolutionCallback(resolution=val).pack()
        ), width=4
    ))
    return InlineKeyboardMarkup(inline_keyboard=ikb)


def select_num_images(values: Iterable[int], current_value: str):
    ikb = [[InlineKeyboardButton(
        text=f'Оставить {current_value}',
        callback_data=SelectNumImagesCallback(num_images=current_value).pack()
    )]]
    ikb.extend(create_list_kb(
        values, get_btn=lambda val: InlineKeyboardButton(
            text=str(val), callback_data=SelectNumImagesCallback(num_images=val).pack()
        ), width=10
    ))
    return InlineKeyboardMarkup(inline_keyboard=ikb)