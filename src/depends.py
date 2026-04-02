from ai.fal.factory import FalFactory
from bot import loader
from config import settings
from payments import PaymentFactory, YooKassaService
from services.payments import PaymentService
from services.storage.s3 import S3ConnectionPool, S3Service, FilesManagerS3

fal_factory = FalFactory(webhook_base_url='')


payment_factory = PaymentFactory(
    yookassa=YooKassaService(
        shop_id=settings.YOOKASSA_SHOP_ID,
        api_token=settings.YOOKASSA_API_KEY
    )
)

payment_service = PaymentService(bot=loader.bot)

s3_pool = S3ConnectionPool()

s3_service = S3Service(s3_pool, settings.S3_BUCKET)

files_manager = FilesManagerS3(s3_service, base_url=f'https://s3.bigling.ru')