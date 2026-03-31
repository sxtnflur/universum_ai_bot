from fastapi import APIRouter, Request
from yookassa.domain.notification import WebhookNotification

from api.depends import PaymentUseCase

router = APIRouter(prefix='/payment')


@router.post('/yookassa')
async def pay_yookassa(
    request: Request,
    payments_use_case: PaymentUseCase
) -> dict:
    payload = WebhookNotification(**await request.json())

    await payments_use_case.on_payment(
        order_id=payload.object.id,
        amount=payload.object.amount.value,
        metadata=payload.object.metadata,
        method='yookassa'
    )
    return {
        'status': 'OK'
    }