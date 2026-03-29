from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot import screens
from data import models
from db.decorator import db_connect
from db.repositories import UsersRepo
from sqlalchemy.ext.asyncio import AsyncSession
from .models import select_model
from ..keyboards.callback_datas.models import SelectModelCallback

router = Router()


@router.message(CommandStart())
@db_connect()
async def start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    *, db: AsyncSession
):
    await state.clear()

    await UsersRepo(db).add_or_update(
        values=dict(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language=message.from_user.language_code,
        ),
        not_update=['id'],
        on_conflict=['id']
    )

    if command and command.args:
        if await process_command_start(
            command.args, message, state
        ):
            return

    await screens.start.menu().answer(message)

    # await screens.models.models_list(
    #     models=list(models.values())[0:10],
    #     page=0,
    #     limit=10
    # ).answer(message)


async def process_command_start(payload: str, message: Message,
                                state: FSMContext) -> bool:
    if payload.startswith('model-'):
        args = payload.split('-')[1:]
        model_name = args[0]
        if len(args) == 2:
            action_type = args[1]
        else:
            action_type = None

        await select_model(
            call=message,
            callback_data=SelectModelCallback(
                key=model_name,
                action_type=action_type
            ),
            state=state
        )
        return True
