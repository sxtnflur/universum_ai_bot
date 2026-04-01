from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TgIdPk, CreatedAt


class User(Base):
    __tablename__ = 'users'

    id: Mapped[TgIdPk]
    username: Mapped[str | None]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    language: Mapped[str | None]
    balance: Mapped[float] = mapped_column(Numeric(10, 2), server_default='0')
    utm: Mapped[str | None]
    created_at: Mapped[CreatedAt]