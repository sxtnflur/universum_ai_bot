from ai.fal.factory import FalFactory
from bot import loader
from config import settings
from payments import PaymentFactory, YooKassaService
from services.payments import PaymentService

fal_factory = FalFactory(webhook_base_url='')


payment_factory = PaymentFactory(
    yookassa=YooKassaService(
        shop_id=settings.YOOKASSA_SHOP_ID,
        api_token=settings.YOOKASSA_API_KEY
    )
)

payment_service = PaymentService(bot=loader.bot)