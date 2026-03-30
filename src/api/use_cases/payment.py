import aiogram
from bot import screens
from db.repositories import UsersRepo, PaymentsRepo
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentUseCase:
    def __init__(self, db: AsyncSession, bot: aiogram.Bot):
        self.db = db
        self.bot = bot

    async def on_payment(self, order_id: str, amount: float, metadata: dict,
                         method: str = 'yookassa') -> None:
        user_id: int = int(metadata['user_id'])
        updated_balance = await UsersRepo(self.db).increase_field(
            filters=dict(id=user_id),
            field='balance',
            value=amount
        )
        await PaymentsRepo(self.db).add(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            method=method
        )
        await self.db.commit()

        await screens.payment.on_payment(
            amount=amount, balance=updated_balance
        ).send_by_id(user_id, self.bot)