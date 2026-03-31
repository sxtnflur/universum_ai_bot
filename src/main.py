import logging
from contextlib import asynccontextmanager
from aiogram.types import Update
from api.app import create_app
from bot.loader import dp, bot
from bot.routers import __routers__
from bot.lifespan import onstartup
from config import settings
from fastapi import FastAPI, BackgroundTasks, Request, HTTPException, Depends

logger = logging.getLogger(__name__)

dp.include_routers(*__routers__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await onstartup(bot)
    await bot.set_webhook(url=settings.BOT_WEBHOOK_URL, request_timeout=60,
                          secret_token=settings.SECRET_TOKEN)
    yield
    await bot.delete_webhook()


def verify_token(request: Request):
    token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if token != settings.SECRET_TOKEN:
        raise HTTPException(status_code=403)


def create_webhook(_=None) -> FastAPI:
    app = create_app(prefix=settings.API_PREFIX, lifespan=lifespan)

    async def feed_update(update: Update):
        await dp.feed_update(bot=bot, update=update)

    @app.post(settings.BOT_WEBHOOK_ENDPOINT)
    async def bot_webhook(request: Request, bg_tasks: BackgroundTasks,
                          _=Depends(verify_token)):
        update = Update.model_validate(await request.json(), context={"bot": bot})
        bg_tasks.add_task(feed_update, update)
    return app


async def start_polling():
    await onstartup()
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(start_polling())