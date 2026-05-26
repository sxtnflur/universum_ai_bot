from services.payments import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession

from utils.price import get_convert_factor


class PaymentUseCase:
    def __init__(self, db: AsyncSession,
                 payment_service: PaymentService):
        self.db = db
        self.payment_service = payment_service

    async def on_payment(self, order_id: str, amount: float, metadata: dict,
                         method: str = 'yookassa') -> None:
        user_id: int = int(metadata['user_id'])
        factor = get_convert_factor('rub')
        await self.payment_service.on_payment(
            user_id=user_id,
            amount=round(amount / factor, 2),
            order_id=order_id,
            method=method,
            db=self.db
        )