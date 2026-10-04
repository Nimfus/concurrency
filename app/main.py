from fastapi import FastAPI
from sqlalchemy import select

from app.db import engine, SessionLocal
from app.models import Base, Inventory
from app.orders import router


app = FastAPI()

Base.metadata.create_all(engine)


@app.on_event("startup")
def seed():
    with SessionLocal.begin() as session:

        existing = session.scalar(select(Inventory).where(Inventory.sku == "SKU-1"))

        if existing is None:
            session.add(Inventory(sku="SKU-1", available=10))


app.include_router(router)
