import dataclasses

import aiogram
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto, \
    ReplyKeyboardRemove
from bot import loader
from typing_extensions import Literal


@dataclasses.dataclass
class ScreenDef:
    text: str | None = None
    photo: str | None = None
    media_group: list[InputMediaPhoto] | None = None
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | None = None
    state: FSMContext | None = None

    @staticmethod
    def __get_fsm(bot_id: int, user_id: int):
        return FSMContext(storage=loader.storage,
                          key=StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id))

    async def answer(self, event: Message | CallbackQuery,
                     type_send: Literal['simple', 'del_msg', 'del_rm', 'edit'] = 'simple',
                     *args, **kwargs
                     ):
        if self.state is not None:
            await self.__get_fsm(event.bot.id, event.from_user.id).set_state(self.state)

        if isinstance(event, Message):
            if self.photo is not None:
                try:
                    if type_send == 'del_msg':
                        await event.delete()
                    elif type_send == 'del_rm':
                        await event.delete_reply_markup()
                except:
                    pass

                await event.answer_photo(
                    photo=self.photo, caption=self.text, reply_markup=self.reply_markup
                )
            elif self.media_group:
                self.media_group[0].caption = self.text
                return await event.answer_media_group(
                    media=self.media_group
                )
            else:
                return await event.answer(
                    text=self.text,
                    reply_markup=self.reply_markup
                )
        else:
            if type_send != 'edit':
                return await self.answer(event.message, type_send)
            try:
                if event.message.photo:
                    if self.photo:
                        await event.message.answer_photo(
                            photo=self.photo, caption=self.text, reply_markup=self.reply_markup
                        )
                        return
                    await event.message.edit_caption(
                        caption=self.text,
                        reply_markup=self.reply_markup
                    )
                else:
                    await event.message.edit_text(
                        text=self.text,
                        reply_markup=self.reply_markup
                    )
            except:
                await self.answer(event.message, type_send)

    async def send_by_id(self, user_id: int, bot: aiogram.Bot):
        if self.state is not None:
            await self.__get_fsm(bot.id, user_id).set_state(self.state)

        if self.photo:
            return await bot.send_photo(
                chat_id=user_id,
                photo=self.photo, caption=self.text,
                reply_markup=self.reply_markup
            )
        elif self.media_group:
            self.media_group[0].caption = self.text
            return await bot.send_media_group(
                chat_id=user_id,
                media=self.media_group
            )
        else:
            return await bot.send_message(
                chat_id=user_id,
                text=self.text, reply_markup=self.reply_markup
            )