import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker, create_async_engine)

from database.models import Base
from dotenv import load_dotenv

load_dotenv()
async_engine = create_async_engine(os.getenv("POSTGRESQL_URL"), echo=True)

async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def update_sequence(tabla_value: str, table_name: str, sequence_name: str):
    async with async_engine.begin() as session:
        # Знайти максимальне значення таблиці
        result = await session.execute(text(f"SELECT MAX({tabla_value}) FROM {table_name}"))
        max_value = result.scalar()

        # Оновити послідовність
        await session.execute(text(f"""
            SELECT setval('{sequence_name}', :max_value + 1, false)
        """), {'max_value': max_value or 0})


async def create_tables():
    async with async_engine.begin() as session:
        await session.run_sync(Base.metadata.create_all)
        async_engine.echo = True


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
