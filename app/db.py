from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
        "postgresql+psycopg://app:app@localhost:5432/fulfillment"
        )

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(
        bind=engine,
        expire_on_commit=False
        )
