import aiogram
from bot import screens
from db.decorator import db_connect
from db.repositories import UsersRepo, PaymentsRepo
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentService:
    def __init__(self, bot: aiogram.Bot):
        self.bot = bot

    @db_connect()
    async def on_payment(self, *, user_id: int, amount: float,
                         method: str, order_id: str,
                         db: AsyncSession):
        updated_balance = await UsersRepo(db).increase_field(
            filters=dict(id=user_id),
            field='balance',
            value=amount
        )
        await PaymentsRepo(db).add(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            method=method
        )
        await db.commit()

        await screens.payment.on_payment(
            amount=amount, balance=updated_balance
        ).send_by_id(user_id, self.bot)