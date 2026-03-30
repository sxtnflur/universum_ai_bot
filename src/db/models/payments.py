from sqlalchemy.orm import Mapped
from .base import Base, IntPk, CreatedAt


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[IntPk]
    order_id: Mapped[str]
    method: Mapped[str]
    user_id: Mapped[int]
    amount: Mapped[float]
    created_at: Mapped[CreatedAt]