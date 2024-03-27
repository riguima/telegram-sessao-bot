from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from telegram_session_bot.database import db


class Base(DeclarativeBase):
    pass


class Payment(Base):
    __tablename__ = 'payments'
    id: Mapped[int] = mapped_column(primary_key=True)
    session_amount: Mapped[int]
    chat_id: Mapped[str]
    payment_id: Mapped[str]


Base.metadata.create_all(db)
