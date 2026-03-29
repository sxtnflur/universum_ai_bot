from api.use_cases.payment import PaymentUseCase
from db.engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

Db = Annotated[AsyncSession, Depends(get_db)]


def get_payment_use_case(db: Db):
    return PaymentUseCase(db=db)


PaymentUseCase = Annotated[PaymentUseCase, Depends(get_payment_use_case)]