from sqlalchemy import BigInteger, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from dotenv import load_dotenv

import os


load_dotenv()
DB_PATH = os.getenv('DB_PATH')

engine = create_async_engine(DB_PATH)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    user_id = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    chat_state: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    companion_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    filters: Mapped[dict] = mapped_column(JSON, nullable=True)
    ready: Mapped[bool] = mapped_column(nullable=True)
    raiting: Mapped[dict] = mapped_column(JSON, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
