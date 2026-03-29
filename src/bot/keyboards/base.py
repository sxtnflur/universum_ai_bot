from typing import Callable, Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback_datas.base import ScrollingCallback
from typing_extensions import T


def create_list_kb(
        objs: Iterable[T], get_btn: Callable[[T], InlineKeyboardButton], width: int = 2
) -> list[list[InlineKeyboardButton]]:
    inl_kb = [[]]
    for obj in objs:
        btn = get_btn(obj)
        if len(inl_kb[-1]) >= width:
            inl_kb.append([btn])
        else:
            inl_kb[-1].append(btn)
    return inl_kb


def create_scrolling_kb(
        page: int,
        limit: int,
        callback_data: type[ScrollingCallback],
        objs: list[T],
        get_btn: Callable[[T], InlineKeyboardButton],
        width: int = 2,
        additional_btns: list[list[InlineKeyboardButton]] | None = None,
        pag_btn_additional_kwargs: dict | None = None,
        pag_left: str = '◀️', pag_right: str = '▶️'
) -> InlineKeyboardMarkup:
    inl_kb = create_list_kb(objs, get_btn, width)
    pag_btns = []

    if page > 0:
        if pag_btn_additional_kwargs:
            pag_btns.append(InlineKeyboardButton(
                text=pag_left,
                callback_data=callback_data(page=page - 1, limit=limit, **pag_btn_additional_kwargs).pack()
            ))
        else:
            pag_btns.append(InlineKeyboardButton(
                text=pag_left, callback_data=callback_data(page=page - 1, limit=limit).pack()
            ))
    if len(objs) == limit:
        print(True)
        if pag_btn_additional_kwargs:
            pag_btns.append(InlineKeyboardButton(
                text=pag_right,
                callback_data=callback_data(page=page + 1, limit=limit, **pag_btn_additional_kwargs).pack()
            ))
        else:
            pag_btns.append(InlineKeyboardButton(
                text=pag_right, callback_data=callback_data(page=page + 1, limit=limit).pack()
            ))
    if pag_btns:
        inl_kb.append(pag_btns)
    if additional_btns:
        inl_kb += additional_btns

    return InlineKeyboardMarkup(inline_keyboard=inl_kb)