import uuid

from sqlalchemy import (
        CheckConstraint,
        Integer,
        String,
        DateTime,
        func
        )
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import(
        DeclarativeBase,
        Mapped,
        mapped_column
        )


class Base(DeclarativeBase):
    pass


class Inventory(Base):
    __tablename__ = "inventory"

    sku: Mapped[str] = mapped_column(Integer, nullable=False, primary_key=True)
    available: Mapped[int] = mapped_column(Integer, nullable=False,)

    __table_args__ = (CheckConstraint("available >= 0", name="inventory_non_negative"),)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(String, unique=True, nullable=False, primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String, unique=True, nullable=False,)
    sku: Mapped[str] = mapped_column(String, nullable=False,)
    qty: Mapped[int] = mapped_column(Integer, nullable=False,)
    status: Mapped[str] = mapped_column(String, nullable=False,)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(),)

    __table_args__ = (CheckConstraint("qty > 0", name="order_qty_positive"),)
