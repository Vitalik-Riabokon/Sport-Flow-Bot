from datetime import datetime
from typing import Any, List, Optional, Tuple
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import update_sequence
from database.models import Users


async def orm_add_user(
        session: AsyncSession,
        telegram_id: int,
        first_name: str,
        last_name: str,
        phone_number: str,
        status: str,
) -> int:
    """
    Додає користувача до бази даних.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        telegram_id (int): Ідентифікатор користувача в Telegram.
        first_name (str): Ім'я користувача.
        last_name (str): Прізвище користувача.
        phone_number (str): Номер телефону користувача.
        status (str): Статус користувача.

    Повертає:
        int: Ідентифікатор доданого користувача.

    Результат:
        Створює новий запис у таблиці користувачів.
    """
    await update_sequence(tabla_value='user_id', table_name='users',
                          sequence_name="users_user_id_seq")
    time_now = datetime.now().date()
    new_user = Users(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        status=status,
        registration_date=time_now,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user.user_id


async def orm_get_user_by_name(
        session: AsyncSession, first_name: str, last_name: str
) -> Optional[Users]:
    """
    Отримує користувача за ім'ям та прізвищем.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        first_name (str): Ім'я користувача.
        last_name (str): Прізвище користувача.

    Повертає:
        Optional[User]: Об'єкт користувача або None, якщо користувача не знайдено.

    Результат:
        Отримує дані про користувача з таблиці користувачів.
    """
    result = await session.execute(
        select(Users).where(
            and_(Users.first_name == first_name, Users.last_name == last_name)
        )
    )
    return result.scalar_one_or_none()


async def orm_get_name(
        session: AsyncSession, telegram_id: int
) -> Optional[Tuple[str, str]]:
    """
    Отримує ім'я та прізвище користувача за його Telegram ID.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        telegram_id (int): Ідентифікатор користувача в Telegram.

    Повертає:
        Optional[Tuple[str, str]]: Кортеж з іменем та прізвищем користувача або None, якщо користувача не знайдено.

    Результат:
        Отримує дані про користувача з таблиці користувачів.
    """
    result = await session.execute(
        select(Users.first_name, Users.last_name).where(
            Users.telegram_id == telegram_id
        )
    )
    return result.fetchone()


async def orm_get_user_by_telegram_id(
        session: AsyncSession, telegram_id: int
) -> Optional[Users]:
    """
    Отримує користувача за його Telegram ID.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        telegram_id (int): Ідентифікатор користувача в Telegram.

    Повертає:
        Optional[User]: Об'єкт користувача або None, якщо користувача не знайдено.

    Результат:
        Отримує дані про користувача з таблиці користувачів.
    """
    print('👉👉')
    result = await session.execute(
        select(Users).where(Users.telegram_id == telegram_id)
    )
    print('👉result', result)
    return result.scalars().one_or_none()


async def orm_get_user_id_by_telegram_id(
        session: AsyncSession, telegram_id: int
) -> Optional[int]:
    """
    Отримує ідентифікатор користувача за його Telegram ID.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        telegram_id (int): Ідентифікатор користувача в Telegram.

    Повертає:
        Optional[int]: Ідентифікатор користувача або None, якщо користувача не знайдено.

    Результат:
        Отримує дані про користувача з таблиці користувачів.
    """
    result = await session.execute(
        select(Users.user_id).where(Users.telegram_id == telegram_id)
    )
    user_id = result.scalar_one_or_none()
    return user_id


async def orm_get_trainer_full_name(
        session: AsyncSession, user_id: int
) -> Optional[Users]:
    """
    Отримує повне ім'я тренера за його ідентифікатором.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача.

    Повертає:
        Optional[Tuple[Users]]: Кортеж з Telegram ID, ім'ям та прізвищем користувача або None, якщо користувача не знайдено.

    Результат:
        Отримує дані про користувача з таблиці користувачів.
    """
    result = await session.execute(
        select(Users).where(
            Users.user_id == user_id))
    res = result.fetchone()
    if res:
        return res[0]
    return None


async def orm_get_telegram_id(session: AsyncSession) -> List[int]:
    """
    Отримує всі Telegram ID користувачів.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.

    Повертає:
        List[int]: Список з усіма Telegram ID користувачів.

    Результат:
        Отримує дані про користувачів з таблиці користувачів.
    """
    result = await session.execute(select(Users.telegram_id))
    return [row[0] for row in result.fetchall()]


async def orm_get_client_telegram_id(session: AsyncSession) -> List[int]:
    """
    Отримує всі Telegram ID користувачів зі статусом 'client'.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.

    Повертає:
        List[int]: Список з усіма Telegram ID користувачів зі статусом 'client'.

    Результат:
        Отримує дані про користувачів з таблиці користувачів.
    """
    result = await session.execute(
        select(Users.telegram_id).where(Users.status == "client")
    )
    return [row[0] for row in result.fetchall()]


async def orm_update_telegram_id(
        session: AsyncSession, new_telegram_id: int, user_id: int
) -> None:
    """
    Оновлює Telegram ID користувача за його ідентифікатором.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        new_telegram_id (int): Новий Telegram ID.
        user_id (int): Ідентифікатор користувача.

    Повертає:
        None

    Результат:
        Оновлює дані користувача у таблиці користувачів.
    """
    result = await session.execute(select(Users).where(Users.user_id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.telegram_id = new_telegram_id
        await session.commit()
