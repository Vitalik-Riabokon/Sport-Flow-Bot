from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import update_sequence
from database.models import Trainer, Users


async def orm_add_trainer(session: AsyncSession, user_id: int) -> None:
    """
    Додає тренера до бази даних.

    Аргументи:
        session (AsyncSession): Асінахронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача, якого треба додати як тренера.

    Повертає:
        None

    Результат:
        Додає запис тренера до таблиці тренерів.
    """
    await update_sequence(tabla_value='trainer_id', table_name='trainers',
                          sequence_name="trainers_trainer_id_seq")
    session.add(Trainer(user_id=user_id))
    await session.commit()


async def orm_get_trainers(session: AsyncSession) -> list[int]:
    """
    Отримує список ідентифікаторів користувачів, які є тренерами.

    Аргументи:
        session (AsyncSession): Асінахронна сесія SQLAlchemy.

    Повертає:
        List[int]: Список ідентифікаторів користувачів.

    Результат:
        Список ідентифікаторів користувачів, які є тренерами.
    """
    result = await session.execute(
        select(Trainer.user_id).join(Users))
    trainers_id = result.scalars().all()
    return trainers_id


async def orm_get_trainer_id_by_user_id(
    session: AsyncSession, user_id: int
) -> Optional[int]:
    """
    Отримує ідентифікатор тренера за ідентифікатором користувача.

    Аргументи:
        session (AsyncSession): Асінахронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача.

    Повертає:
        Optional[int]: Ідентифікатор тренера або None, якщо тренера не знайдено.

    Результат:
        Ідентифікатор тренера за ідентифікатором користувача.
    """
    result = await session.execute(
        select(Trainer.trainer_id).where(Trainer.user_id == user_id)
    )
    trainer_id = result.scalar_one_or_none()
    return trainer_id


async def orm_get_trainer_details(session: AsyncSession, trainer_id: int) -> list[dict]:
    """
    Отримує детальну інформацію про тренера за його ідентифікатором.

    Аргументи:
        session (AsyncSession): Асінахронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.

    Повертає:
        List[dict]: Список словників з детальною інформацією про тренера.

    Результат:
        Список словників, кожен з яких містить:
            - user_id (int): Ідентифікатор користувача.
            - telegram_id (int): Ідентифікатор Telegram.
            - first_name (str): Ім'я.
            - last_name (str): Прізвище.
            - phone_number (str): Номер телефону.
            - status (str): Статус.
    """
    result = await session.execute(
        select(
            Users.user_id,
            Users.telegram_id,
            Users.first_name,
            Users.last_name,
            Users.phone_number,
            Users.status,
        )
        .join(Trainer)
        .where(Trainer.trainer_id == trainer_id)
    )
    trainer_data = result.mappings().all()
    return [dict(row) for row in trainer_data]
