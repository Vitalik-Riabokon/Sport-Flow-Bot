from datetime import datetime
from typing import List, Optional, Tuple, Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, sessionmaker

from database.engine import update_sequence
from database.models import TrainerClient, Users


# Функції для роботи з базою даних


async def orm_add_trainer_clients(
        session: AsyncSession, trainer_id: int, client_id: int, price_per_session: float
) -> None:
    """
    Додає запис у таблицю trainer_clients.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        price_per_session (float): Ціна за сеанс.
    """
    await update_sequence(tabla_value='id', table_name='trainer_clients',
                          sequence_name="trainer_clients_id_seq")
    time_now = datetime.now().date()
    new_record = TrainerClient(
        trainer_id=trainer_id,
        client_id=client_id,
        price_per_session=price_per_session,
        start_date=time_now,
    )
    session.add(new_record)
    await session.commit()


async def orm_get_client_id(session: AsyncSession) -> List[int]:
    """
    Отримує всі унікальні ідентифікатори клієнтів, у яких end_date is NULL.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.

    Повертає:
        List[int]: Список унікальних ідентифікаторів клієнтів.
    """
    result = await session.execute(
        select(TrainerClient.client_id)
        .distinct()
        .where(TrainerClient.end_date.is_(None))
    )
    return [row[0] for row in result.fetchall()]


async def orm_get_client_full_name_tg_id(
        session: AsyncSession, trainer_id: int
) -> List[Tuple[int, str, str]]:
    """
    Отримує Telegram ID, ім'я та прізвище клієнтів для даного тренера.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.

    Повертає:
        List[Tuple[int, str, str]]: Список з даними клієнтів.
    """
    result = await session.execute(
        select(Users.telegram_id, Users.first_name, Users.last_name)
        .join(TrainerClient, TrainerClient.client_id == Users.user_id)
        .where(TrainerClient.trainer_id == trainer_id, TrainerClient.end_date.is_(None))
    )
    return result.fetchall()


async def orm_get_client_data(
        session: AsyncSession, client_telegram_id: int
) -> List[Tuple[int, int, int, str, str, str, float, datetime.date, datetime.date]]:
    """
    Отримує дані клієнта за його Telegram ID.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_telegram_id (int): Telegram ID клієнта.

    Повертає:
        List[Tuple[int, int, int, str, str, str, float, datetime.date, datetime.date]]: Список з даними клієнта.
    """
    result = await session.execute(
        select(
            TrainerClient.client_id,
            TrainerClient.trainer_id,
            Users.telegram_id,
            Users.first_name,
            Users.last_name,
            Users.phone_number,
            TrainerClient.price_per_session,
            TrainerClient.start_date,
            TrainerClient.end_date,
        )
        .join(Users, TrainerClient.client_id == Users.user_id)
        .where(Users.telegram_id == client_telegram_id)
    )
    return result.fetchall()


async def orm_get_trainer_id(session: AsyncSession, client_id: int) -> Optional[int]:
    """
    Отримує ідентифікатор тренера за ідентифікатором клієнта.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_id (int): Ідентифікатор клієнта.

    Повертає:
        Optional[int]: Ідентифікатор тренера або None, якщо тренера не знайдено.
    """
    result = await session.execute(
        select(TrainerClient.trainer_id).where(TrainerClient.client_id == client_id)
    )
    return result.scalar_one_or_none()


async def orm_update_end_data_client(session: AsyncSession, client_id: int) -> None:
    """
    Оновлює end_date клієнта.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_id (int): Ідентифікатор клієнта.
    """
    time_now = datetime.now().date()
    await session.execute(
        update(TrainerClient)
        .where(TrainerClient.client_id == client_id)
        .values(end_date=time_now)
    )
    await session.commit()


async def orm_update_client(
        session: AsyncSession, trainer_id: int, client_id: int, price_per_session: float
) -> None:
    """
    Оновлює дані клієнта.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        price_per_session (float): Ціна за сеанс.
    """
    time_now = datetime.now().date()
    await session.execute(
        update(TrainerClient)
        .where(TrainerClient.client_id == client_id)
        .values(
            trainer_id=trainer_id,
            price_per_session=price_per_session,
            start_date=time_now,
            end_date=None,
        )
    )
    await session.commit()


async def orm_update_price_per_session(
        session: AsyncSession, client_id: int, price_per_session: float
) -> None:
    """
    Оновлює ціну за сеанс для клієнта.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_id (int): Ідентифікатор клієнта.
        price_per_session (float): Нова ціна за сеанс.
    """
    await session.execute(
        update(TrainerClient)
        .where(TrainerClient.client_id == client_id)
        .values(price_per_session=price_per_session)
    )
    await session.commit()
