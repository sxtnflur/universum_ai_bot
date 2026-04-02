import datetime
import textwrap
from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import keyboards
from bot.keyboards.base import create_list_kb
from bot.keyboards.callback_datas.models import ScrollModelsCallback, SelectRatioCallback, SelectResolutionCallback, \
    SelectInputNumberParamCallback
from bot.screens.base import ScreenDef
from config import settings
from data import Model
from mytypes import ActionType
from utils import prepare_strings


def types_to_strings(types: list[str | tuple[str, str]], model_key: str,
                     exclude: Iterable[str] | None = None) -> str | None:
    types_ = []
    for t in types:
        if isinstance(t, tuple):
            if exclude and t[0] in exclude:
                continue

            types_.append(
                f'<a href="https://t.me/{settings.BOT_USERNAME}?start=model-{model_key}-{t[0]}">'
                f'{prepare_strings.action_type(t[1])}</a>'
            )
        else:
            if exclude and t in exclude:
                continue

            types_.append(
                f'<a href="https://t.me/{settings.BOT_USERNAME}?start=model-{model_key}-{t}">'
                f'{prepare_strings.action_type(t)}</a>'
            )
    if not types_:
        return
    return ', '.join(types_)


def models_list(models: list[Model],
                page: int = 0,
                limit: int = 10):
    text = ''

    for model in models:
        text += f'\n\n<b>{model.title}</b>:\n' + types_to_strings(model.types, model.key)

    return ScreenDef(
        text=text,
        reply_markup=keyboards.models.models_list(
            page, limit, []
        )
    )


def __settings(
    model: Model,
    action_type: ActionType,
):
    text = f'''
<blockquote><b>Модель:</b> {model.title}
<b>Выбранный тип генерации:</b> {prepare_strings.action_type(action_type)}'''

    other_types = types_to_strings(model.types, model.key, exclude=(action_type,))
    if other_types:
        text += '\n\n<b>Другие типы генерации:</b>\n' + other_types
    return text + '\n\n<b>Выбрать другую модель:</b> /models\n<b>В меню:</b> /start' + '</blockquote>'


def ask_prompt(
    model: Model,
    action_type: ActionType
):
    return ScreenDef(
        text=f'''
{__settings(model, action_type)}

<i>Отправьте ваш промпт:</i>
'''
    )


def ask_images(
    model: Model,
    action_type: ActionType,
    min_count_images: int | None = None,
    max_count_images: int | None = None
):
    text = __settings(model, action_type) + '\n\n'
    if max_count_images is not None:
        if max_count_images == 1:
            text += f'<i>Отправьте 1 изображение</i>'
        else:
            text += f'<i>Отправьте от {min_count_images or 1} до {max_count_images} изображений</i>'
    elif min_count_images:
        text += f'<i>Отправьте от {min_count_images} изображений</i>'
    else:
        text += f'<i>Отправьте изображения:</i>'

    return ScreenDef(
        text=text
    )


def prepare_to_generation(
    model: Model,
    price: float,
    num_images: int = 1,
    max_num_images: int = 1,
    prompt: str | None = None,
    images_count: int | None = None,
    ratio: str | None = None,
    resolution: str | None = None,
    upscale_factor: float | None = None,
    noise_scale: float | None = None,

    price_description: str | None = None,
    **kwargs
):
    text = f'<b>Модель:</b> {model.title}'
    if prompt:
        text += f'\n<b>Промпт:</b> {textwrap.shorten(prompt, width=100)}'
    if images_count:
        text += f'\n<b>Фото:</b> {images_count}'

    ikb = [[
        InlineKeyboardButton(
            text='Сгенерировать',
            callback_data='start-generate'
        )
    ]]
    if ratio is not None:
        text += f'\n<b>Соотн. сторон:</b> {ratio}'
        ikb.append([InlineKeyboardButton(
            text=ratio, callback_data='select-ratio'
        )])
    if resolution is not None:
        text += f'\n<b>Качество:</b> {resolution}'
        ikb.append([InlineKeyboardButton(
            text=resolution, callback_data='select-resolution'
        )])
    if upscale_factor is not None:
        text += f'\n<b>Коэффициент улучшения (Upscale Factor):</b> {upscale_factor}'
        ikb.append([InlineKeyboardButton(
            text=f'Коэф. улучш.: {upscale_factor}',
            callback_data=SelectInputNumberParamCallback(
                param='upscale_factor'
            ).pack()
        )])
    if noise_scale is not None:
        text += f'\n<b>Noise Scale (шкала шума):</b> {noise_scale}'
        ikb.append([InlineKeyboardButton(
            text=f'Noise Scale: {noise_scale}',
            callback_data=SelectInputNumberParamCallback(
                param='noise_scale'
            ).pack()
        )])

    if max_num_images > 1:
        ikb.append([InlineKeyboardButton(
            text=f'Количество фото: {num_images}',
            callback_data='select-num_images'
        )])

    text += f'\n<b>Количество фото:</b> {num_images}'
    text += f'\n\n<b>Стоимость:</b> {round(price, 2)} ⚡️'
    if num_images > 1:
        text += f' <i>({round(price / num_images, 2)} ⚡️ за каждую)</i>'

    if price_description:
        text += f'\n<blockquote><b>Как рассчитывается цена?</b>\n{price_description}</blockquote>'

    text += '\n\n<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> ' \
            'Вы можете сразу начать генерацию по кнопке "Сгенерировать" или указать доп. настройки кнопками ниже'
    text += '\n<blockquote>Выбрать другую модель: /models\nВ меню: /start</blockquote>'
    return ScreenDef(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb)
    )


def not_enough_balance(
    balance: float,
    need: float
):
    return ScreenDef(
        text=f'''
❌ К сожалению, на вашем балансе недостаточно средств

<b>Ваш баланс:</b> {balance}
<b>Стоимость генерации:</b> {need}

<b>Пополнить баланс:</b> /buy
'''
    )


def on_success_generation(
    model_title: str,
    action_type_title: str,
    amount: float,
    updated_balance: float
):
    return ScreenDef(
        text=f'''
<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> Генерация для модели <b>{model_title} ({action_type_title})</b> выполнена

<b>Генерация стоила:</b> {amount} ⚡️
<b>Текущий баланс:</b> {updated_balance} ⚡️'''
    )


def _on_failed_gen(
    request_id: str | None = None,
    model_info: str | None = None
):
    text = f'<blockquote>'
    if model_info is not None:
        text += f'<b>Модель:</b> {model_info}'
    if request_id is not None:
        text += f'<b>ID запроса:</b> <code>{request_id}</code>\n'
    text += f'<b>Время ошибки (UTC):</b> {datetime.datetime.utcnow().strftime("%H:%M %d.%m.%Y")}</blockquote>'
    return text


def on_failed_sending_generation(
    support_url: str, delay: int,
    model_info: str | None = None,
    request_id: str | None = None,
    last_attempt: bool = False
):
    print(f'screens: {request_id=}')
    return ScreenDef(
        text=f'<b>Произошла ошибка при отправке результата генерации</b>\n'
             + (f'Повторная попытка отправки будет через <i>{delay}</i> секунд\n' if not last_attempt
                else '') +
             f'Если ждете слишком долго, перешлите это сообщение в поддержку: {support_url}\n\n'
             f'{_on_failed_gen(request_id, model_info)}'
    )


def on_failed_generation(
    support_url: str,
    request_id: str | None = None,
    model_info: str | None = None
):
    return ScreenDef(
        text=f'<b>Произошла ошибка во время генерации. '
             f'Пожалуйста, перешлите это сообщение в поддержку: {support_url}</b>\n\n'
             f'{_on_failed_gen(request_id, model_info)}'
    )


def send_result_as_links(
    links: list[str]
):
    if len(links) == 1:
        return ScreenDef(
            text='Результат генерации получился слишком многовесным, поэтому отправить его в Telegram не удалось. '
                 'Пожалуйста, <b>скачайте по кнопкам ниже.</b>\n'
                 'Ссылка перестанет работать через <b>24 часа</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text='Скачать', url=links[0]
                )]
            ])
        )
    return ScreenDef(
        text='Результат генерации получился слишком многовесным, поэтому отправить его в Telegram не удалось. '
             'Пожалуйста, <b>скачайте по кнопкам ниже.</b>\n'
             'Ссылки перестанут работать через <b>24 часа</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=create_list_kb(
            objs=links, get_btn=lambda link: InlineKeyboardButton(
                text='Скачать файл #' + str(links.index(link)+1),
                url=link
            ),
            width=5
        ))
    )