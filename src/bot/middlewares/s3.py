from typing import *
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from services.storage.s3 import S3Service


class S3Middleware(BaseMiddleware):
    def __init__(self, s3_service: S3Service):
        self.s3_service = s3_service

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        data.update(s3=self.s3_service)
        return await handler(event, data)