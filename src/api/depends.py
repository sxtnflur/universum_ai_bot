from api.use_cases.payment import PaymentUseCase
from bot import loader
from db.engine import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

Db = Annotated[AsyncSession, Depends(get_db)]


def get_payment_use_case(db: Db):
    return PaymentUseCase(db=db, bot=loader.bot)


PaymentUseCase = Annotated[PaymentUseCase, Depends(get_payment_use_case)]