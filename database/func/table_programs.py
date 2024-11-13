from datetime import datetime
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import update_sequence
from database.models import Program


async def orm_add_program(
    session: AsyncSession,
    trainer_id: int,
    client_id: int,
    program_file: str,
    program_date: datetime,
) -> int:
    """
    Додає нову програму до бази даних.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        program_file (str): Файл програми.
        program_date (datetime): Дата програми.

    Повертає:
        int: Ідентифікатор нової програми.
    """
    await update_sequence(tabla_value='program_id', table_name='programs',
                          sequence_name="programs_program_id_seq")
    new_program = Program(
        trainer_id=trainer_id,
        client_id=client_id,
        program_file=program_file,
        program_date=program_date,
    )
    session.add(new_program)
    await session.commit()
    return new_program.program_id


async def orm_check_program(
    session: AsyncSession, trainer_id: int, client_id: int, program_date: datetime
) -> Optional[Program]:
    """
    Перевіряє наявність програми для даного тренера, клієнта та дати.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        program_date (datetime): Дата програми.

    Повертає:
        Optional[Programs]: Програма або None, якщо програма не знайдена.
    """
    result = await session.execute(
        select(Program)
        .where(Program.trainer_id == trainer_id)
        .where(Program.client_id == client_id)
        .where(Program.program_date == program_date)
    )
    return result.scalar_one_or_none()


async def orm_get_program(
    session: AsyncSession, trainer_id: int, client_id: int, program_date: datetime
) -> Optional[str]:
    """
    Отримує файл програми для даного тренера, клієнта та дати.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        program_date (datetime): Дата програми.

    Повертає:
        Optional[str]: Файл програми або None, якщо програма не знайдена.
    """
    result = await session.execute(
        select(Program.program_file)
        .where(Program.trainer_id == trainer_id)
        .where(Program.client_id == client_id)
        .where(Program.program_date == program_date)
    )
    program_file = result.scalar_one_or_none()
    return program_file


async def orm_del_program(
    session: AsyncSession, trainer_id: int, client_id: int, program_date: datetime
) -> None:
    """
    Видаляє програму для даного тренера, клієнта та дати.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        program_date (datetime): Дата програми.
    """
    try:
        await session.execute(
            delete(Program)
            .where(Program.trainer_id == trainer_id)
            .where(Program.client_id == client_id)
            .where(Program.program_date == program_date)
        )
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_check_all_training(
    session: AsyncSession, trainer_id: int, client_id: int, month: int
) -> list[int]:
    """
    Перевіряє всі тренування для даного тренера та клієнта в заданому місяці.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        client_id (int): Ідентифікатор клієнта.
        month (int): Номер місяця.

    Повертає:
        List[int]: Список днів місяця, коли були тренування.
    """
    current_year = datetime.now().year
    start_date = datetime(current_year, month, 1)
    if month == 12:
        end_date = datetime(current_year + 1, 1, 1)
    else:
        end_date = datetime(current_year, month + 1, 1)

    result = await session.execute(
        select(func.to_char(Program.program_date, 'DD').label("day"))
        .where(Program.trainer_id == trainer_id)
        .where(Program.client_id == client_id)
        .where(Program.program_date >= start_date)
        .where(Program.program_date < end_date)
        .order_by(Program.program_date)
    )

    return [int(row.day) for row in result]
