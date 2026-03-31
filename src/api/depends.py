from api.use_cases.payment import PaymentUseCase
from bot import loader
from db.engine import get_db
from depends import payment_service
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from api.use_cases.ai import AIUseCase

Db = Annotated[AsyncSession, Depends(get_db)]


def get_payment_use_case(db: Db):
    return PaymentUseCase(db=db, payment_service=payment_service)


PaymentUseCase = Annotated[PaymentUseCase, Depends(get_payment_use_case)]


def get_ai_use_case(db: Db):
    return AIUseCase(db=db, bot=loader.bot)


AIUseCase = Annotated[AIUseCase, Depends(get_ai_use_case)]
