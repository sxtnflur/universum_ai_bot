from services.payments import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentUseCase:
    def __init__(self, db: AsyncSession,
                 payment_service: PaymentService):
        self.db = db
        self.payment_service = payment_service

    async def on_payment(self, order_id: str, amount: float, metadata: dict,
                         method: str = 'yookassa') -> None:
        user_id: int = int(metadata['user_id'])
        await self.payment_service.on_payment(
            user_id=user_id,
            amount=amount,
            order_id=order_id,
            method=method,
            db=self.db
        )