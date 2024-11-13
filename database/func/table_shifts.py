from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import update_sequence
from database.func.table_users import orm_get_name, orm_get_user_by_telegram_id
from database.models import Shift


async def orm_open_shift(session: AsyncSession, telegram_id: int) -> int:
    """
    Відкриває зміну для користувача з заданим Telegram ID.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        telegram_id (int): Ідентифікатор користувача в Telegram.

    Повертає:
        int: Ідентифікатор відкритої зміни.

    Результат:
        Створює новий запис у таблиці змін з заданими параметрами.
    """
    # Отримати ім'я та прізвище користувача за telegram_id
    user = await orm_get_user_by_telegram_id(session, telegram_id)
    await update_sequence(tabla_value='id', table_name='shifts',
                          sequence_name="shifts_id_seq")
    # Створити новий запис у таблиці змін
    new_shift = Shift(
        user_id=user.user_id,
        start_time=datetime.now().date(),
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(new_shift)
    await session.commit()
    await session.refresh(new_shift)
    return new_shift.id


async def orm_close_shift(session: AsyncSession, shift_id: int) -> None:
    """
    Закриває зміну з заданим ідентифікатором.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        shift_id (int): Ідентифікатор зміни.

    Повертає:
        None

    Результат:
        Оновлює час закінчення зміни у відповідному записі.
    """
    result = await session.execute(select(Shift).where(Shift.id == shift_id))
    shift = result.scalar_one_or_none()
    if shift:
        shift.end_time = datetime.now()
        await session.commit()


async def orm_get_active_shift(session: AsyncSession) -> Optional[Shift]:
    """
    Отримує активну зміну, яка ще не закрита.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.

    Повертає:
        Optional[Tuple[int, int, str]]: Кортеж з ідентифікатора зміни, Telegram ID та імені користувача або None, якщо немає активних змін.

    Результат:
        Отримує дані про активну зміну з таблиці змін.
    """

    result = await session.execute(
        select(Shift).where(
            Shift.end_time == None
        )
    )
    res = result.fetchone()
    if res:
        return res[0]
    return None
