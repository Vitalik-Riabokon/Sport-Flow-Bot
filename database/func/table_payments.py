from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func, select, exists
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import in_

from database.engine import update_sequence
from database.models import (Payment, Product, Trainer, TrainerClient,
                             TrainingSession, Users)


async def orm_add_payment(
        session: AsyncSession,
        user_id: int,
        product_id: int,
        payment_method: str,
        price: float,
        expiration_date: str,
) -> int:
    """
    Додає новий платіж до бази даних.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача.
        product_id (int): Ідентифікатор продукту.
        payment_method (str): Метод оплати.
        price (float): Ціна.
        expiration_date (str): Дата закінчення.

    Повертає:
        int: Ідентифікатор нового платежу.
    """
    try:
        # Оновлюємо послідовність перед додаванням нових записів
        await update_sequence(tabla_value='payment_id', table_name='payments', sequence_name='payments_payment_id_seq')

        new_payment = Payment(
            user_id=user_id,
            product_id=product_id,
            payment_method=payment_method,
            price=price,
            payment_date=datetime.now().date(),
            expiration_date=expiration_date,
        )
        session.add(new_payment)
        await session.commit()
        return new_payment.payment_id
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_get_expiration_date(
        session: AsyncSession, user_id: int
) -> Optional[Tuple[int, str, str]]:
    """
    Отримує дату закінчення підписки для користувача.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача.

    Повертає:
        Optional[Tuple[int, str, str]]: Кортеж (ID продукту, дата платежу, дата закінчення) або None, якщо не знайдено.
    """
    time_now = datetime.now().date()
    result = await session.execute(
        select(Payment.product_id, Payment.payment_date, Payment.expiration_date)
        .join(Product, Product.product_id == Payment.product_id)
        .where(
            Payment.expiration_date > time_now,
            Payment.user_id == user_id,
            Product.category == "membership",
        )
    )
    return result.fetchone()


async def orm_get_last_payment(
        session: AsyncSession, user_id: int
) -> Optional[Tuple[str, float, str, str]]:
    """
    Отримує останній платіж для користувача.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача.

    Повертає:
        Optional[Tuple[str, float, str, str]]: Кортеж (назва продукту, ціна, метод оплати, дата платежу) або None, якщо не знайдено.
    """
    result = await session.execute(
        select(
            Product.product_name,
            Payment.price,
            Payment.payment_method,
            Payment.payment_date,
        )
        .join(Product, Product.product_id == Payment.product_id)
        .where(Payment.user_id == user_id)
        .order_by(Payment.payment_date.desc())
    )
    return result.fetchone()


async def orm_get_validity_memberships(
        session: AsyncSession,
) -> List[Tuple[str, str, str, float, str, str]]:
    """
    Отримує інформацію про дійсні підписки.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.

    Повертає:
        List[Tuple[str, str, str, float, str, str]]: Список кортежів з інформацією про дійсні підписки.
    """
    current_date = datetime.now().date()
    date_four_days_ago = current_date - timedelta(days=4)
    date_in_four_days = current_date + timedelta(days=4)

    subquery = (
        select(Payment.product_id)
        .select_from(Payment)
        .join(Product)
        .where(Product.category == "membership")
        .scalar_subquery()
    )

    query = (
        select(
            Users.telegram_id,
            Users.first_name,
            Users.last_name,
            Users.phone_number,
            Product.product_name,
            Payment.price,
            Payment.payment_date,
            Payment.expiration_date,
        )
        .select_from(Payment)
        .join(Product, Product.product_id == Payment.product_id)
        .join(Users, Users.user_id == Payment.user_id)
        .where(Payment.product_id.in_(subquery))
        .where(
            func.date(Payment.expiration_date).between(date_four_days_ago, current_date)
            | func.date(Payment.expiration_date).between(
                current_date, date_in_four_days
            )
        )
        .where(
            ~exists(
                select(1)
                .select_from(Payment)
                .join(Product, Product.product_id == Payment.product_id)
                .where(Payment.user_id == Users.user_id)
                .where(Payment.expiration_date > Payment.expiration_date)
            )
        )
    )

    result = await session.execute(query)
    return result.fetchall()


async def orm_get_count_one_time_training(
        session: AsyncSession, user_id: int
) -> Tuple[int, float]:
    """
    Отримує кількість і суму однократних тренувань для користувача за місяць.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        user_id (int): Ідентифікатор користувача.

    Повертає:
        Tuple[int, float]: Кількість однократних тренувань і загальна сума.
    """
    current_date = datetime.now().date()
    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = first_day_of_month.replace(
        month=first_day_of_month.month % 12 + 1
    ) - timedelta(days=1)

    result = await session.execute(
        select(func.count(), func.sum(Payment.price))
        .join(Product, Product.product_id == Payment.product_id)
        .where(Payment.user_id == user_id, Product.category == "one_time_training")
        .where(Payment.payment_date.between(first_day_of_month, last_day_of_month))
    )
    return result.fetchone()


async def orm_get_income(
        session: AsyncSession,
        type_data: str,
        month_number: Optional[int] = None,
        day_number: Optional[int] = None,
        category_filter: Optional[List[str]] = None,
        telegram_id: Optional[str] = None,
) -> List[Tuple[float, str]]:
    """
    Отримує дохід за певний період.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        type_data (str): Тип даних ('day', 'month', 'year').
        month_number (Optional[int]): Номер місяця (для типу 'month').
        day_number (Optional[int]): Номер дня (для типу 'day').
        category_filter (Optional[List[str]]): Список категорій для фільтрації.
        telegram_id (Optional[str]): Telegram ID для фільтрації.

    Повертає:
        List[Tuple[float, str]]: Список кортежів (загальний дохід, метод оплати).
    """
    current_date = datetime.now().date()

    if type_data == "day":
        start_date = end_date = (
            datetime(current_date.year, current_date.month, day_number).date()
            if day_number
            else current_date
        )
    elif type_data == "month":
        if month_number:
            start_date = datetime(current_date.year, month_number, 1).date()
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
        else:
            start_date = current_date.replace(day=1)
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
    elif type_data == "year":
        start_date = datetime(current_date.year, 1, 1).date()
        end_date = datetime(current_date.year, 12, 31).date()
    else:
        raise ValueError("Invalid type_data. Use 'day', 'month', or 'year'.")

    query = (
        select(func.sum(Payment.price), Payment.payment_method)
        .join(Product, Product.product_id == Payment.product_id)
        .where(Payment.payment_date.between(start_date, end_date))
    )

    params = [start_date, end_date]

    if category_filter:
        query = query.where(Product.category.in_(category_filter))

    if telegram_id:
        subquery = (
            select([1])
            .join(TrainerClient, TrainerClient.client_id == TrainingSession.client_id)
            .join(Trainer, Trainer.trainer_id == TrainingSession.trainer_id)
            .join(Users, Users.user_id == Trainer.user_id)
            .where(Users.telegram_id == telegram_id)
            .where(TrainingSession.session_date.between(start_date, end_date))
            .exists()
        )
        query = query.where(subquery)

    query = query.group_by(Payment.payment_method)

    result = await session.execute(query)
    return result.fetchall()


async def orm_get_person_gym(
        session: AsyncSession, month_number: int, day_number: int, switch: bool = False
) -> List[Tuple[str, str, Optional[str], float, str]]:
    """
    Отримує статистику по людям у залі за певну дату.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        month_number (int): Номер місяця.
        day_number (int): Номер дня.
        switch (bool): Якщо True, то фільтрує тренування за категорією ('membership', 'one_time_training').

    Повертає:
        List[Tuple[str, str, str, float, str]]: Список кортежів з інформацією про тренування.
    """
    start_date = end_date = datetime(
        datetime.now().year, month_number, day_number
    ).date()

    if switch:
        query = (
            select(
                Users.first_name,
                Users.last_name,
                Product.product_name,
                Payment.price,
                Payment.payment_method,
            )
            .join(Product, Product.product_id == Payment.product_id)
            .join(Users, Users.user_id == Payment.user_id)
            .where(Payment.payment_date.between(start_date, end_date))
            .where(Product.category.notin_(["membership", "one_time_training"]))
        )
    else:
        query = (
            select(
                Users.first_name, Users.last_name, Payment.price, Payment.payment_method
            )
            .join(Product, Product.product_id == Payment.product_id)
            .join(Users, Users.user_id == Payment.user_id)
            .where(Payment.payment_date.between(start_date, end_date))
            .where(Product.category.in_(["membership", "one_time_training"]))
        )

    result = await session.execute(query)
    return result.fetchall()


async def orm_get_months_with_data(session: AsyncSession, type_statistic: str,
                                   telegram_id: int = None):
    """
    Отримує місяці, для яких є дані в базі даних, згідно з типом статистики.

    :param session: Асинхронна сесія SQLAlchemy для виконання запитів.
    :param type_statistic: Тип статистики. Може бути 'gym', 'goods' або 'client'.
    :param telegram_id: (Необов'язковий) Telegram ID користувача для статистики клієнтів.
    :return: Множина місяців, для яких є дані, у вигляді цілих чисел.
    """
    if type_statistic == "gym" or type_statistic == "goods":
        category_filter = ('membership', 'one_time_training')
        if type_statistic == "gym":
            result = await session.execute(
                select(func.extract('month', Payment.payment_date).label('month'))
                .join(Product, Product.product_id == Payment.product_id)
                .filter(Product.category.in_(category_filter))
                .group_by(func.extract('month', Payment.payment_date))
            )
            months_with_data = {row.month for row in result}
        else:
            result = await session.execute(
                select(func.extract('month', Payment.payment_date).label('month'))
                .join(Product, Product.product_id == Payment.product_id)
                .filter(Product.category.notin_(category_filter))
                .group_by(func.extract('month', Payment.payment_date))
            )
            months_with_data = {row.month for row in result}
    elif type_statistic == "client":
        trainer_subquery = (
            select(Trainer.trainer_id)
            .join(Users, Trainer.user_id == Users.user_id)
            .where(Users.telegram_id == telegram_id)
            .scalar_subquery()
        )

        result = await session.execute(
            select(func.extract('month', TrainingSession.session_date).label('month'))
            .join(Trainer, TrainingSession.trainer_id == Trainer.trainer_id)
            .where(TrainingSession.trainer_id == trainer_subquery)
            .group_by(func.extract('month', TrainingSession.session_date))
        )
        months_with_data = {row.month for row in result}

    else:
        months_with_data = set()

    return months_with_data


async def orm_get_days_with_data(session: AsyncSession, type_statistic: str, month: int,
                                 telegram_id: int = None):
    """
    Отримує дні місяця, для яких є дані в базі даних, згідно з типом статистики.

    :param session: Асинхронна сесія SQLAlchemy для виконання запитів.
    :param type_statistic: Тип статистики. Може бути 'gym', 'goods' або 'client'.
    :param month: Місяць для фільтрації даних.
    :param telegram_id: (Необов'язковий) Telegram ID користувача для статистики клієнтів.
    :return: Множина днів місяця, для яких є дані, у вигляді цілих чисел.
    """
    days_with_data = set()

    if type_statistic == "gym" or type_statistic == "goods":
        category_filter = ('membership', 'one_time_training')
        if type_statistic == "gym":
            result = await session.execute(
                select(func.extract('day', Payment.payment_date).label('day'))
                .join(Product, Product.product_id == Payment.product_id)
                .filter(Product.category.in_(category_filter),
                        func.extract('month', Payment.payment_date) == month)
                .group_by(func.extract('day', Payment.payment_date))
            )
            days_with_data = {row.day for row in result}
        else:
            result = await session.execute(
                select(func.extract('day', Payment.payment_date).label('day'))
                .join(Product, Product.product_id == Payment.product_id)
                .filter(Product.category.notin_(category_filter),
                        func.extract('month', Payment.payment_date) == month)
                .group_by(func.extract('day', Payment.payment_date))
            )
            days_with_data = {row.day for row in result}

    elif type_statistic == "client":
        trainer_subquery = (
            select(Trainer.trainer_id)
            .join(Users, Trainer.user_id == Users.user_id)
            .where(Users.telegram_id == telegram_id)
            .scalar_subquery()
        )

        result = await session.execute(
            select(func.extract('day', TrainingSession.session_date).label('day'))
            .join(Trainer, TrainingSession.trainer_id == Trainer.trainer_id)
            .where(
                TrainingSession.trainer_id == trainer_subquery,
                func.extract('month', TrainingSession.session_date) == month
            )
            .group_by(func.extract('day', TrainingSession.session_date))
        )

        days_with_data = {row.day for row in result}

    return days_with_data
