from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from database.engine import update_sequence
from database.models import (Trainer, TrainerClient, TrainingSession, Users)


async def orm_add_session(
    session: AsyncSession,
    client_id: int,
    trainer_id: int,
    price_session: float,
    payment_method: str,
) -> None:
    """
    Додає запис у таблицю training_sessions.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_id (int): Ідентифікатор клієнта.
        trainer_id (int): Ідентифікатор тренера.
        price_session (float): Ціна за сеанс.
        payment_method (str): Метод оплати.
    """
    await update_sequence(tabla_value='session_id', table_name='training_sessions',
                          sequence_name="training_sessions_session_id_seq")
    time_now = datetime.now().date()
    new_record = TrainingSession(
        client_id=client_id,
        trainer_id=trainer_id,
        price_session=price_session,
        payment_method=payment_method,
        session_date=time_now,
    )
    session.add(new_record)
    await session.commit()


async def orm_get_count_visiting(
    session: AsyncSession, client_id: int
) -> Tuple[int, float]:
    """
    Отримує кількість відвідувань і загальну суму за сеанси для даного клієнта в поточному місяці.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_id (int): Ідентифікатор клієнта.

    Повертає:
        Tuple[int, float]: Кількість відвідувань та загальна сума за сеанси.
    """
    current_date = datetime.now()
    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = (
        first_day_of_month.replace(month=first_day_of_month.month % 12 + 1)
        - timedelta(days=1)
    ).date()

    result = await session.execute(
        select(
            func.count(TrainingSession.session_id),
            func.sum(TrainingSession.price_session),
        )
        .where(TrainingSession.client_id == client_id)
        .where(
            TrainingSession.session_date.between(first_day_of_month, last_day_of_month)
        )
    )
    return result.fetchone()


async def orm_get_session_date_visiting(session: AsyncSession, client_id: int) -> str:
    """
    Отримує дати сеансів для даного клієнта в поточному місяці у відформатованому вигляді.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        client_id (int): Ідентифікатор клієнта.

    Повертає:
        str: Відформатовані дати сеансів, згруповані за тижнями.
    """
    current_date = datetime.now()
    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = (
            first_day_of_month.replace(month=first_day_of_month.month % 12 + 1)
            - timedelta(days=1)
    ).date()

    result = await session.execute(
        select(TrainingSession.session_date)
        .join(TrainerClient, TrainingSession.client_id == TrainerClient.client_id)
        .where(TrainingSession.client_id == client_id)
        .where(
            TrainingSession.session_date.between(first_day_of_month, last_day_of_month)
        )
    )
    session_dates = result.fetchall()

    if session_dates:
        dates = [date[0] for date in session_dates]
        df = pd.DataFrame({"date": dates})

        # Переконаємося, що 'date' - це datetime
        df['date'] = pd.to_datetime(df['date'])

        df["week_number"] = df["date"].dt.isocalendar().week
        df["day_number"] = df["date"].dt.strftime("%d")
        df["day_name"] = df["date"].dt.strftime("%a")
        days_translation = {
            "Mon": "Пн",
            "Tue": "Вт",
            "Wed": "Ср",
            "Thu": "Чт",
            "Fri": "Пт",
            "Sat": "Сб",
            "Sun": "Нд",
        }
        df["day_name"] = df["day_name"].map(days_translation)
        df["formatted"] = df["day_name"] + "-" + df["day_number"]
        weeks = df.groupby("week_number")["formatted"].apply(list).to_dict()
        output = ""
        for week, days in weeks.items():
            output += " ".join(days) + "\n"
        return output
    return ""


async def orm_get_sessions_today(
    session: AsyncSession,
    trainer_id: int,
    month_number: Optional[int] = None,
    day_number: Optional[int] = None,
) -> List[Tuple[str, str, str, str, float]]:
    """
    Отримує дані сеансів для даного тренера на сьогодні.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        trainer_id (int): Ідентифікатор тренера.
        month_number (Optional[int]): Номер місяця для перевірки (за замовчуванням None).
        day_number (Optional[int]): Номер дня для перевірки (за замовчуванням None).

    Повертає:
        List[Tuple[str, str, str, str, float]]: Список з даними клієнтів і сеансів.
    """
    time_now = datetime.now().date()
    if day_number is not None:
        time_now = time_now.replace(month=month_number, day=day_number)

    result = await session.execute(
        select(
            Users.first_name,
            Users.last_name,
            Users.phone_number,
            TrainingSession.payment_method,
            TrainingSession.price_session,
        )
        .join(TrainerClient, TrainingSession.client_id == TrainerClient.client_id)
        .join(Users, TrainerClient.client_id == Users.user_id)
        .where(TrainingSession.trainer_id == trainer_id)
        .where(TrainingSession.session_date == time_now)
    )
    return result.fetchall()


async def orm_get_client_income(
    session: AsyncSession,
    telegram_id: int,
    type_data: str,
    month_number: Optional[int] = None,
    day_number: Optional[int] = None,
) -> List[Tuple[float, str]]:
    """
    Отримує дохід клієнта за заданий період.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        telegram_id (int): Telegram ID клієнта.
        type_data (str): Тип періоду ("day", "month" або "year").
        month_number (Optional[int]): Номер місяця для перевірки (за замовчуванням None).
        day_number (Optional[int]): Номер дня для перевірки (за замовчуванням None).

    Повертає:
        List[Tuple[float, str]]: Список з загальним доходом та методом оплати.
    """
    current_date = datetime.now().date()

    if type_data == "day":
        if day_number is not None:
            start_date = datetime(datetime.now().year, month_number, day_number)
            start_date = end_date = start_date.date()
        else:
            start_date = end_date = current_date
    elif type_data == "month":
        if month_number is not None:
            year = datetime.now().year
            start_date = datetime(year, month_number, 1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
            start_date, end_date = start_date.date(), end_date.date()
        else:
            start_date = current_date.replace(day=1)
            next_month = current_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)

    elif type_data == "year":
        start_date = current_date.replace(month=1, day=1)
        end_date = current_date.replace(month=12, day=31)
    else:
        raise ValueError("Invalid type_data. Use 'day', 'month', or 'year'.")

    result = await session.execute(
        select(
            func.sum(TrainingSession.price_session),
            TrainingSession.payment_method,
        )
        .select_from(TrainingSession)
        .join(Trainer, TrainingSession.trainer_id == Trainer.trainer_id)
        .join(TrainerClient, TrainingSession.client_id == TrainerClient.client_id)
        .join(Users, Trainer.user_id == Users.user_id)
        .where(Users.telegram_id == telegram_id)
        .where(TrainingSession.session_date.between(start_date, end_date))
        .group_by(TrainingSession.payment_method)
    )
    return result.fetchall()