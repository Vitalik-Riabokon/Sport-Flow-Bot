from typing import List, Optional, Tuple

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import update_sequence
from database.models import Product


async def orm_add_product(
        session: AsyncSession, product_name: str, price: float, category: str
) -> int:
    """
    Додає новий продукт до бази даних.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_name (str): Назва продукту.
        price (float): Ціна продукту.
        category (str): Категорія продукту.

    Повертає:
        int: Ідентифікатор нового продукту.
    """
    try:
        await update_sequence(tabla_value='product_id', table_name='products', sequence_name='products_product_id_seq')
        new_product = Product(product_name=product_name, price=price, category=category)
        session.add(new_product)
        await session.commit()
        return new_product.product_id
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_get_all_categories(session: AsyncSession) -> List[str]:
    """
    Отримує всі унікальні категорії продуктів.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.

    Повертає:
        List[str]: Список унікальних категорій продуктів.
    """
    result = await session.execute(select(Product.category).distinct())
    return [row[0] for row in result]


async def orm_update_category(
        session: AsyncSession, old_category: str, new_category: str
) -> None:
    """
    Оновлює категорію продуктів з однієї категорії на іншу.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        old_category (str): Стара категорія.
        new_category (str): Нова категорія.
    """
    try:
        await session.execute(
            update(Product)
            .where(Product.category == old_category)
            .values(category=new_category)
        )
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_update_product(
        session: AsyncSession, product_name: str, update_name: str, update_type: str | float
) -> None:
    """
    Оновлює властивість продукту.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_name (str): Назва продукту.
        update_name (str): Назва властивості для оновлення.
        update_value (str): Нове значення властивості.
    """
    try:
        await session.execute(
            update(Product)
            .where(Product.product_name == product_name)
            .values({update_name: update_type})
        )
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_get_product_price(
        session: AsyncSession, product_name: str
) -> Optional[float]:
    """
    Отримує ціну продукту за його назвою.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_name (str): Назва продукту.

    Повертає:
        Optional[float]: Ціна продукту або None, якщо продукт не знайдено.
    """
    result = await session.execute(
        select(Product.price).where(Product.product_name == product_name)
    )
    price = result.scalar_one_or_none()
    return price


async def orm_get_product_description(
        session: AsyncSession, product_name: str
) -> Optional[str]:
    """
    Отримує опис продукту за його назвою.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_name (str): Назва продукту.

    Повертає:
        Optional[str]: Опис продукту або None, якщо продукт не знайдено.
    """
    result = await session.execute(
        select(Product.description).where(Product.product_name == product_name)
    )
    description = result.scalar_one_or_none()
    return description


async def orm_get_product_id_category(
        session: AsyncSession, product_name: str
) -> Optional[Product]:
    """
    Отримує ідентифікатор продукту та категорію за його назвою.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_name (str): Назва продукту.

    Повертає:
        Optional[Tuple[int, str]]: Кортеж (ідентифікатор продукту,ціна продукта, категорія) або None, якщо продукт не знайдено.
    """
    result = await session.execute(
        select(Product).where(
            Product.product_name == product_name
        )
    )
    res = result.fetchone()
    if res:
        return res[0]
    return None


async def orm_get_all_category(session: AsyncSession, bloc: bool = True) -> List[str]:
    """
    Отримує всі категорії продуктів, виключаючи деякі специфічні категорії.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        bloc (bool): Якщо True, виключає категорії зі статусом "membership" і "one_time_training".

    Повертає:
        List[str]: Список категорій продуктів.
    """
    query = (
        select(Product.category)
        .distinct()
        .where(Product.category.notin_(["membership", "one_time_training"]))
    )
    if bloc:
        query = query.where(Product.status_product.is_(None))

    result = await session.execute(query)
    return [row[0] for row in result]


async def orm_get_product_name_by_category(
        session: AsyncSession, category: str, bloc: bool = False
) -> List[str]:
    """
    Отримує всі назви продуктів за категорією.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        category (str): Категорія продукту.

    Повертає:
        List[str]: Список назв продуктів у заданій категорії.
    """
    if bloc:
        result = await session.execute(
            select(Product.product_name).where(
                Product.category == category, Product.status_product.is_not(None)
            )
        )
        print('🚫🚫result',result)
        if result:
            return [row[0] for row in result]
        return result

    else:
        result = await session.execute(
            select(Product.product_name).where(
                Product.category == category, Product.status_product.is_(None)
            )
        )

    return [row[0] for row in result]


async def orm_get_data_by_product_id(
        session: AsyncSession, product_id: int
) -> Optional[Tuple[str, float]]:
    """
    Отримує назву продукту та ціну за ідентифікатором продукту.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_id (int): Ідентифікатор продукту.

    Повертає:
        Optional[Tuple[str, float]]: Кортеж (назва продукту, ціна) або None, якщо продукт не знайдено.
    """
    result = await session.execute(
        select(Product.product_name, Product.price).where(
            Product.product_id == product_id
        )
    )
    return result.fetchone()


async def orm_status_product_column(
        session: AsyncSession, column: str, status_product: str | None, column_value: str
) -> None:
    """
    Оновлює статус продукту для заданого значення в колонці.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        column (str): Назва колонки для фільтрації.
        status_product (str): Статус продукту для оновлення.
        column_value (str): Значення колонки для фільтрації.
    """
    try:
        await session.execute(
            update(Product)
            .where(getattr(Product, column) == column_value)
            .values(status_product=status_product)
        )
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e


async def orm_get_product_details(
        session: AsyncSession, product_name: str
) -> Optional[Tuple[str, str, float, str]]:
    """
    Отримує деталі продукту за його назвою.

    Аргументи:
        session (AsyncSession): Асинхронна сесія SQLAlchemy.
        product_name (str): Назва продукту.

    Повертає:
        Optional[Tuple[str, str, float, str]]: Кортеж (опис, фото, ціна, категорія) або None, якщо продукт не знайдено.
    """
    result = await session.execute(
        select(
            Product.description, Product.photo, Product.price, Product.category
        ).where(Product.product_name == product_name)
    )
    return result.fetchone()
