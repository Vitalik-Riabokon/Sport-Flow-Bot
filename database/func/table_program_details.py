from typing import List, Tuple

import pandas as pd
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import update_sequence
from database.models import ProgramDetail


async def orm_add_program_details(
        session: AsyncSession, program_id: int, read_excel_file: pd.DataFrame
) -> None:
    """
    Додає деталі програми з файлу Excel до бази даних.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        program_id (int): Ідентифікатор програми.
        read_excel_file (pd.DataFrame): Дані з файлу Excel.
    """
    try:
        await update_sequence(tabla_value='program_details_id', table_name='program_details',
                              sequence_name='program_details_program_details_id_seq')
        print('🚫read_excel_file.iterrows()', read_excel_file.iterrows())
        for index, row in read_excel_file.iterrows():
            new_detail = ProgramDetail(
                program_id=program_id,
                training_number=row["Тренировка№"],
                approaches_number=str(row["Кількість підходів"]),
                repetitions_number=str(row["Повтори"]),
                weight=row["169,9"],
                program_status=None
            )
            session.add(new_detail)
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        print(e)
        raise e


async def orm_check_program_details(
        session: AsyncSession, program_id: int
) -> List[int]:
    """
    Перевіряє наявність деталей програми для даного ідентифікатора програми.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        program_id (int): Ідентифікатор програми.

    Повертає:
        List[int]: Список категорій (ідентифікаторів деталей програми).
    """
    result = await session.execute(
        select(ProgramDetail.program_details_id).where(
            ProgramDetail.program_id == program_id
        )
    )
    return [row[0] for row in result]


async def orm_get_program_details_training_number(
        session: AsyncSession, program_id: int
) -> List[int]:
    """
    Отримує унікальні номери тренувань для даного ідентифікатора програми.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        program_id (int): Ідентифікатор програми.

    Повертає:
        List[int]: Список унікальних номерів тренувань.
    """
    result = await session.execute(
        select(ProgramDetail.training_number)
        .distinct()
        .where(ProgramDetail.program_id == program_id)
        .order_by(ProgramDetail.training_number.asc())
    )
    return [row[0] for row in result]


async def orm_get_program_details_data(
        session: AsyncSession, program_id: int, training_number: int
) -> List[Tuple[int, int, float]]:
    """
    Отримує дані деталей програми для заданого номера тренування та ідентифікатора програми.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        program_id (int): Ідентифікатор програми.
        training_number (int): Номер тренування.

    Повертає:
        List[Tuple[int, int, float]]: Список даних (кількість підходів, кількість повторів, вага).
    """
    result = await session.execute(
        select(
            ProgramDetail.approaches_number,
            ProgramDetail.repetitions_number,
            ProgramDetail.weight,
        )
        .where(ProgramDetail.training_number == training_number)
        .where(ProgramDetail.program_id == program_id)
    )
    return result.fetchall()


async def orm_check_completed_days(
        session: AsyncSession, program_id: int
) -> List[Tuple[int, str]]:
    """
    Перевіряє дні, в які була завершена програма для даного ідентифікатора програми.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        program_id (int): Ідентифікатор програми.

    Повертає:
        List[Tuple[int, str]]: Список даних (номер тренування, статус програми).
    """
    result = await session.execute(
        select(ProgramDetail.training_number, ProgramDetail.program_status)
        .where(ProgramDetail.program_id == program_id)
        .where(ProgramDetail.program_status.isnot(None))
        .distinct()
    )
    return result.fetchall()


async def orm_update_status_program_details(
        session: AsyncSession, program_id: int, training_number: int, program_status: str
) -> None:
    """
    Оновлює статус програми для даного ідентифікатора програми та номера тренування.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        program_id (int): Ідентифікатор програми.
        training_number (int): Номер тренування.
        program_status (str): Новий статус програми.
    """
    try:
        await session.execute(
            update(ProgramDetail)
            .where(ProgramDetail.program_id == program_id)
            .where(ProgramDetail.training_number == training_number)
            .values(program_status=program_status)
        )
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_del_program_details(session: AsyncSession, program_id: int) -> None:
    """
    Видаляє всі деталі програми з таблиці `ProgramDetail`, що відповідають заданому `program_id`.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy для взаємодії з базою даних.
        program_id (int): Ідентифікатор програми, деталі якої потрібно видалити.

    Повертає:
        None: Функція не повертає жодного значення.
    """

    # Видалення всіх записів у таблиці `ProgramDetail`, де `program_id` відповідає заданому значенню
    await session.execute(delete(ProgramDetail).where(ProgramDetail.program_id == program_id))

    # Застосування змін до бази даних
    await session.commit()
