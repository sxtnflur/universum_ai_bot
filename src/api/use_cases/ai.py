import aiogram
from aiogram.types import InputMediaPhoto, URLInputFile, InputMediaDocument
from api.schemas import FalRequest
from db.repositories import GenerationRequestsRepo, UsersRepo
from sqlalchemy.ext.asyncio import AsyncSession


async def _send_images(bot: aiogram.Bot, chat_id: int, images: list[dict], text: str | None = None):
    await bot.send_media_group(
        chat_id=chat_id,
        media=[InputMediaPhoto(
            media=URLInputFile(media['url']),
            caption=text if i == 0 else None
        ) for i, media in enumerate(images)]
    )
    await bot.send_media_group(
        chat_id=chat_id,
        media=[
            InputMediaDocument(media=URLInputFile(media['url'], filename=media['file_name']))
            for i, media in enumerate(images)
        ]
    )


async def _send_image(bot: aiogram.Bot, chat_id: int, image: dict, text: str | None = None):
    await bot.send_photo(
        chat_id=chat_id,
        photo=URLInputFile(image['url']),
        caption=text
    )
    await bot.send_document(
        chat_id=chat_id,
        document=URLInputFile(image['url'], filename=image['file_name'])
    )


async def _send_message(
    bot: aiogram.Bot, chat_id: int, payload: dict
):
    if 'images' in payload:
        if len(payload['images']) > 1:
            await _send_images(bot=bot, chat_id=chat_id, images=payload['images'],
                               text=payload.get('description'))
        else:
            await _send_image(bot=bot, chat_id=chat_id, image=payload['images'][0],
                              text=payload.get('description'))

    elif 'image' in payload:
        await _send_image(
            bot=bot, chat_id=chat_id,
            image=payload['image'],
            text=payload.get('description')
        )

    elif 'text' in payload:
        await bot.send_message(
            chat_id=chat_id,
            text=payload['text']
        )


class AIUseCase:
    def __init__(self, db: AsyncSession, bot: aiogram.Bot):
        self.bot = bot
        self.db = db

    async def on_fal_request(self, data: FalRequest) -> None:
        payload: dict = data.payload

        request = await GenerationRequestsRepo(self.db).get_one(request_id=data.request_id)
        user_id: int = request.user_id
        amount: float = request.amount

        await _send_message(bot=self.bot, chat_id=user_id, payload=payload)

        updated_balance = await UsersRepo(self.db).decrease_field(
            filters=dict(id=user_id),
            field='balance',
            value=amount
        )
        await self.bot.send_message(
            chat_id=user_id,
            text=f'''
-{amount} ⚡️

<b>Текущий баланс:</b> {updated_balance} ⚡️'''
        )