from config import settings
from depends import s3_pool
from services.storage import S3Service
from .commands import set_my_commands
from .loader import bot, dp
from .middlewares import S3Middleware


async def onstartup(*args, **kwargs):
    await set_my_commands(bot=bot)
    await s3_pool.initialize(
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        bucket=settings.S3_BUCKET,
        max_pool_connections=50
    )
    s3 = S3Service(s3_pool, settings.S3_BUCKET)