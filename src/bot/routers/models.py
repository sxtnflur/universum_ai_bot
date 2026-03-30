import asyncio
from typing import Callable, get_origin, Annotated

import aiogram
from PIL import Image
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument, URLInputFile
from aiogram.exceptions import TelegramAPIError
import inspect
from typing import get_args

from db.decorator import db_connect
from db.repositories import UsersRepo
from depends import fal_factory
from mytypes import ActionType
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from utils.do_while import send_action_while_do_func
from utils.inspect_func import inspect_generation_func, GenFuncInfo
from utils.price import process_amount
from utils.retry import async_retry
from .. import screens, keyboards

from ..keyboards.callback_datas.models import ScrollModelsCallback, SelectModelCallback, SelectRatioCallback, \
    SelectResolutionCallback, SelectNumImagesCallback, SelectInputNumberParamCallback
from data import models
from ..middlewares.media_group import MediaMiddleware
from bot.menu import MODELS

router = Router()
router.message.middleware(MediaMiddleware(2))


class GenerationStates(StatesGroup):
    prompt = State()
    image = State()
    input_num_param = State()


@router.message(Command('models'))
@router.message(F.text == MODELS)
async def models_list_m(
    message: Message
):
    await models_list(
        message, ScrollModelsCallback()
    )


@router.callback_query(ScrollModelsCallback.filter())
async def models_list(
        call: CallbackQuery,
        callback_data: ScrollModelsCallback
):
    offset = callback_data.page * callback_data.limit
    models_ = list(models.values())[offset:callback_data.limit]
    await screens.models.models_list(
        models=models_,
        page=callback_data.page,
        limit=callback_data.limit
    ).answer(call, 'edit')


@router.callback_query(SelectModelCallback.filter())
async def select_model(
        call: CallbackQuery,
        callback_data: SelectModelCallback,
        state: FSMContext
):

    model = models[callback_data.key]

    if callback_data.action_type is None:
        action_type = model.types[0]
    else:
        action_type = callback_data.action_type

    await state.clear()
    await state.update_data(model_key=callback_data.key,
                            action_type=action_type)

    fal_service = fal_factory.get_model_by_key(callback_data.key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)
    await ask_next_param(
        call, state,
        model=callback_data.key,
        action_type=action_type,
        func_info=func_info
    )

    try:
        await call.answer()
    except:
        pass


@router.message(GenerationStates.prompt)
async def get_prompt(
        message: Message, state: FSMContext
):
    if not message.text:
        await message.answer(
            'Отправьте ваш промпт:'
        )
        return

    await state.update_data(prompt=message.text)
    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)
    await ask_next_param(
        message, state,
        model=model_key,
        action_type=action_type,
        func_info=func_info,
        fsm_data=data
    )


@router.message(GenerationStates.image)
async def get_image(
        message: Message, state: FSMContext,
        media_group: list[Message] | None = None
):
    if not message.photo:
        await message.answer(
            'Отправьте изображения:'
        )
        return

    if media_group:
        images = [msg.photo[-1].file_id for msg in media_group]
    else:
        images = [message.photo[-1].file_id]

    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)

    if func_info.min_images and len(images) < func_info.min_images:
        await message.answer(
            f'Нужно отправить от {func_info.min_images or 1} '
            f'{f"до {func_info.max_images} " if func_info.max_images else ""}'
            f'изображений.\n'
            f'Вы отправили {len(images)}\n\n'
            f'Отправьте все изображения еще раз:'
        )
        return

    if func_info.max_images and len(images) > func_info.max_images:
        await message.answer(
            f'Нужно отправить от {func_info.min_images or 1} '
            f'{f"до {func_info.max_images} " if func_info.max_images else ""}'
            f'изображений.\n'
            f'Вы отправили {len(images)}\n\n'
            f'Отправьте все изображения еще раз:'
        )
        return

    await state.update_data(images=images)
    data['images'] = images

    await ask_next_param(
        message, state,
        model=model_key,
        action_type=action_type,
        func_info=func_info,
        fsm_data=data
    )


async def ask_next_param(
    message: CallbackQuery | Message,
    state: FSMContext,
    model: str | None = None,
    action_type: ActionType | None = None,
    func_info: GenFuncInfo | None = None,
    fsm_data: dict | None = None
):
    if not fsm_data:
        fsm_data = await state.get_data()

    if model is None:
        model = fsm_data['model_key']
    if action_type is None:
        action_type = fsm_data['action_type']

    if func_info is None:
        fal_service = fal_factory.get_model_by_key(model)
        func: Callable = getattr(fal_service, action_type)
        func_info = inspect_generation_func(func)

    if model is None or action_type is None or func_info is None:
        raise Exception('Не указан model/action_type/func_info в ask_next_param()')

    model = models[model]

    if 'images' in func_info.required_arguments and fsm_data.get('images') is None:
        await screens.models.ask_images(
            model, action_type,
            min_count_images=func_info.min_images,
            max_count_images=func_info.max_images
        ).answer(message)
        await state.set_state(GenerationStates.image)
        return

    if 'prompt' in func_info.required_arguments and fsm_data.get('prompt') is None:
        await screens.models.ask_prompt(model, action_type).answer(message)
        await state.set_state(GenerationStates.prompt)
        return

    kwargs = {}
    for k, v in func_info.arguments.items():
        val = fsm_data.get(k)
        if not val:
            val = func_info.arguments[k].default
        kwargs[k] = val

    if 'images' in kwargs:
        kwargs['images'] = [Image.open(await message.bot.download(file=img_file_id))
         for img_file_id in kwargs.get('images')]

    fal_service = fal_factory.get_model_by_key(model.key)
    price: float = fal_service.get_price(
        func=func_info.func, kwargs=kwargs
    )

    price_description: str | None = fal_service.get_price_description(func_info.func, kwargs)

    await screens.models.prepare_to_generation(
        model=model,
        max_num_images=func_info.max_input_num_images,
        images_count=len(fsm_data.get('images')) if fsm_data.get('images') else None,
        price=price,
        price_description=price_description,
        **kwargs
    ).answer(message, 'edit')


@router.callback_query(F.data == 'select-ratio')
async def select_ratio(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)

    if 'ratio' in func_info.arguments:
        ratio = data.get('ratio')
        if not ratio:
            ratio = func_info.arguments['ratio'].default

        values = get_args(func_info.arguments['ratio'].annotation)
        values = [v for v in values if v != ratio]
        await call.message.edit_reply_markup(
            reply_markup=keyboards.models.select_ratio(values, ratio)
        )


@router.callback_query(SelectRatioCallback.filter())
async def update_ratio(
    call: CallbackQuery, callback_data: SelectRatioCallback,
    state: FSMContext
):
    await state.update_data(ratio=callback_data.ratio.replace('-', ':'))
    data = await state.get_data()
    model = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)
    await ask_next_param(
        message=call, state=state,
        model=model,
        action_type=action_type,
        func_info=func_info
    )


@router.callback_query(F.data == 'select-resolution')
async def select_resolution(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)

    if 'resolution' in func_info.arguments:
        resolution = data.get('resolution')
        if not resolution:
            resolution = func_info.arguments['resolution'].default

        values = get_args(func_info.arguments['resolution'].annotation)
        values = [v for v in values if v != resolution]
        await call.message.edit_reply_markup(
            reply_markup=keyboards.models.select_resolution(values, resolution)
        )


@router.callback_query(SelectResolutionCallback.filter())
async def update_resolution(
    call: CallbackQuery, callback_data: SelectResolutionCallback,
    state: FSMContext
):
    await state.update_data(resolution=callback_data.resolution)
    data = await state.get_data()
    model = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)
    await ask_next_param(
        message=call, state=state,
        model=model,
        action_type=action_type,
        func_info=func_info
    )


@router.callback_query(F.data == 'select-num_images')
async def select_num_images(
    call: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)

    if 'num_images' in func_info.arguments:
        num_images = data.get('num_images')
        if not num_images:
            num_images = func_info.arguments['num_images'].default

        values = [v for v in
                  range(func_info.min_input_num_images, func_info.max_input_num_images+1)
                  if v != num_images]
        await call.message.edit_reply_markup(
            reply_markup=keyboards.models.select_num_images(
                current_value=num_images, values=values
            )
        )


@router.callback_query(SelectNumImagesCallback.filter())
async def select_num_images(
    call: CallbackQuery,
    callback_data: SelectNumImagesCallback,
    state: FSMContext
):
    await state.update_data(num_images=callback_data.num_images)
    data = await state.get_data()
    model = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)
    await ask_next_param(
        message=call, state=state,
        model=model,
        action_type=action_type,
        func_info=func_info
    )


@router.callback_query(SelectInputNumberParamCallback.filter())
async def select_input_num_param(
        call: CallbackQuery,
        callback_data: SelectInputNumberParamCallback,
        state: FSMContext
):
    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']
    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)
    func_info = inspect_generation_func(func)
    annotation = get_args(func_info.arguments[callback_data.param].annotation)
    type_ = annotation[0]

    min_val = getattr(annotation[1].metadata, 'ge', None)
    max_val = getattr(annotation[1].metadata, 'le', None)
    only_int = isinstance(type_, int)

    if min_val:
        text = f'Введите значение от {min_val}'
        if max_val:
            text += f' до {max_val}'
    elif max_val:
        text = f'Введите значение до {max_val}'
    else:
        text = 'Введите значение'

    if only_int:
        text += ' (число должно быть круглым: 1/2/3 <s>1.5</s>)'
    else:
        text += ' (число может быть нецелым: 1/1.1/1.2/.../2/2.1/...)'
    await call.message.answer(text)
    await state.update_data(
        wait_param=callback_data.param,
        wait_param_min=min_val,
        wait_param_max=max_val,
        wait_param_only_int=only_int
    )
    await state.set_state(GenerationStates.input_num_param)


@router.message(GenerationStates.input_num_param)
async def input_num_param(
    message: Message, state: FSMContext
):
    try:
        val = float(message.text)
    except:
        await message.answer('Вы ввели не число')
        return

    data = await state.get_data()
    if data.get('only_int'):
        try:
            val = int(val)
        except:
            await message.answer('Можно ввести только целое число')
            return

    if data.get('wait_param_min') and val < data.get('wait_param_min'):
        await message.answer(f'Минимальное значение: {data.get("wait_param_min")}')
        return

    if data.get('wait_param_max') and val > data.get('wait_param_max'):
        await message.answer(f'Максимальное значение: {data.get("wait_param_max")}')
        return

    data[data['wait_param']] = val
    del data['wait_param']
    del data['wait_param_min']
    del data['wait_param_max']
    del data['wait_param_only_int']

    await state.set_state(None)
    await state.update_data(data)
    await ask_next_param(
        message=message, state=state,
        fsm_data=data
    )


@router.callback_query(F.data == 'start-generate')
async def start_generate(
        call: CallbackQuery, state: FSMContext
):
    await call.message.delete_reply_markup()

    data = await state.get_data()
    model_key = data['model_key']
    action_type = data['action_type']

    fal_service = fal_factory.get_model_by_key(model_key)
    func: Callable = getattr(fal_service, action_type)

    func_info = inspect_generation_func(func)

    amount: float = round(fal_service.get_price(
        func=func_info.func, kwargs=data
    ) * data.get('num_images', 1), 2)

    @db_connect()
    async def get_balance(db: AsyncSession):
        return await UsersRepo(db).get_one_field('balance', id=call.from_user.id)
    balance = await get_balance()
    if balance < amount:
        await screens.models.not_enough_balance(balance, amount).answer(call)
        return

    f = inspect.signature(func)
    kwargs = {k: v for k, v in data.items() if k in f.parameters}
    if 'images' in kwargs:
        kwargs.update(
            images=[Image.open(await call.bot.download(file=img_file_id))
                    for img_file_id in kwargs.get('images')]
        )

    if action_type.endswith('image'):
        action = 'upload_photo'
    elif action_type.endswith('text'):
        action = 'typing'
    elif action_type.endswith('video'):
        action = 'upload_video'
    elif action_type.endswith('audio'):
        action = 'upload_voice'
    else:
        action = 'typing'

    wait_msg = await call.message.answer('Подождите немного, сейчас я все сделаю...')

    res = await send_action_while_do_func(
        coroutine=func(**kwargs), chat_id=call.message.chat.id,
        bot=call.bot, action=action
    )
    try:
        await wait_msg.delete()
    except:
        pass
    await send_result(res, bot=call.bot, chat_id=call.message.chat.id)

    @db_connect()
    async def decrease(db: AsyncSession):
        return await UsersRepo(db).decrease_field(
            filters=dict(id=call.from_user.id),
            field='balance',
            value=amount
        )

    updated_balance = await decrease()

    await call.message.answer(
        text=f'''
-{amount} ⚡️

<b>Текущий баланс:</b> {updated_balance} ⚡️'''
    )


@async_retry(
    attempts=50, delay=60,
    exceptions=(asyncio.TimeoutError, asyncio.CancelledError, TelegramAPIError),
    backoff=2
)
async def send_result(res: dict, bot: aiogram.Bot, chat_id: int):
    if 'images' in res:
        if len(res['images']) > 1:
            await bot.send_media_group(
                chat_id=chat_id,
                media=[InputMediaPhoto(media=URLInputFile(media),
                                       caption=res.get('text')) for i, media in enumerate(res['images'])]
            )
            await bot.send_media_group(
                chat_id=chat_id,
                media=[InputMediaDocument(
                    media=URLInputFile(media, filename=media.split('/')[-1]),
                    caption=res.get('text')) for i, media in enumerate(res['images'])
                ]
            )
        else:
            await bot.send_photo(
                chat_id=chat_id,
                photo=URLInputFile(res['images'][0]),
                caption=res.get('text')
            )
            await bot.send_document(
                chat_id=chat_id,
                document=URLInputFile(res['images'][0], filename=res['images'][0].split('/')[-1]),
                caption=res.get('text')
            )
    elif 'text' in res:
        await bot.send_message(
            chat_id=chat_id,
            text=res['text']
        )
