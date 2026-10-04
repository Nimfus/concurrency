from fastapi import APIRouter, HTTPException
from fastapi.params import Header
from psycopg.types import uuid
from pydantic import BaseModel
from sqlalchemy import text
from app.db import SessionLocal
import uuid

router = APIRouter()


class CreateOrderRequest(BaseModel):
    sku: str
    qty: int


class OrderResponse(BaseModel):
    id: uuid.UUID
    sku: str
    qty: int
    status: str


@router.post("/orders", response_model=OrderResponse)
def create_order(request: CreateOrderRequest, idempotency_key: str = Header(alias="Idempotency-Key"),
                 fail_after_reserve: bool = Header(False, alias="X-Lab-Fail-After-Reserve")):
    order_id = uuid.uuid4()

    with SessionLocal.begin() as session:
        inserted = session.execute(
            text(
                """INSERT INTO orders (id, idempotency_key, sku, qty, status) VALUES (:id, :key, :sku, :qty, 'PENDING') ON CONFLICT (idempotency_key) DO NOTHING RETURNING id"""),
            {"id": order_id, "key": idempotency_key, "sku": request.sku, "qty": request.qty}
        ).scalar_one_or_none()

        if inserted is None:
            existing = session.execute(text("""SELECT id, sku, qty, status FROM orders WHERE idempotency_key = :key"""),
                                       {"key": idempotency_key}).mappings().one()

            if (existing["sku"] != request.sku or existing["qty"] != request.qty):
                raise HTTPException(status_code=409, detail=("Idempotency key reused with different payload"))

            return OrderResponse(**existing)

        remaining = session.execute(text("""UPDATE inventory SET available = available - :qty
        WHERE sku = :sku AND available >= :qty RETURNING available"""),
                                    {"qty": request.qty, "sku": request.sku}).scalar_one_or_none()

        if remaining is None:
            session.execute(text("""UPDATE orders SET status = 'REJECTED_OUT_OF_STOCK' WHERE id = :id"""),
                                 {"id": order_id})
            status = 'REJECTED_OUT_OF_STOCK'
        else:
            if fail_after_reserve:
                raise RuntimeError("Injected failure")

            session.execute(text("""UPDATE orders SET status = 'CONFIRMED' where id = :id"""), {"id": order_id})
            status = 'CONFIRMED'

        return OrderResponse(
            id=order_id,
            sku=request.sku,
            qty=request.qty,
            status=status
        )
