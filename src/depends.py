from ai.fal.factory import FalFactory
from payments import PaymentFactory, YooKassaService

fal_factory = FalFactory(webhook_base_url='')


payment_factory = PaymentFactory(
    yookassa=YooKassaService(
        shop_id=...,
        api_token=...
    )
)