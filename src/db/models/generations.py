from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, IntPk


class GenerationRequest(Base):
    __tablename__ = 'generation_requests'

    id: Mapped[IntPk]
    request_id: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[int]
    amount: Mapped[float]