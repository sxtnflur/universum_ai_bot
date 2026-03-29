import aiogram
from bot import screens
from db.repositories import UsersRepo
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentUseCase:
    def __init__(self, db: AsyncSession, bot: aiogram.Bot):
        self.db = db
        self.bot = bot

    async def on_payment(self, amount: float, metadata: dict) -> None:
        user_id: int = metadata['user_id']
        updated_balance = await UsersRepo(self.db).increase_field(
            filters=dict(id=user_id),
            field='balance',
            value=amount
        )
        await screens.payment.on_payment(
            amount=amount, balance=updated_balance
        ).send_by_id(user_id, self.bot)