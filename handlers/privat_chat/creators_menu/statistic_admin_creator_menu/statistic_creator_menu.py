from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.creator_menu_button import check_details_menu_button
from database.func.table_payments import orm_get_income
from database.func.table_products import orm_get_all_categories
from database.func.table_training_sessions import orm_get_client_income
from middlewares.Safe_memory import ChatDataMiddleware

creator_statistic_router = Router()


async def get_gym_income(session, type_data, month_number=None, day_number=None):
    return await orm_get_income(
        session=session,
        type_data=type_data,
        month_number=month_number,
        day_number=day_number,
        category_filter=["membership", "one_time_training"],
    )


async def get_goods_income(session, type_data, month_number=None, day_number=None):
    all_categories = await orm_get_all_categories(session=session)
    exclude_categories = ["membership", "one_time_training"]
    categories = [cat for cat in all_categories if cat not in exclude_categories]
    return await orm_get_income(
        session=session,
        type_data=type_data,
        month_number=month_number,
        day_number=day_number,
        category_filter=categories,
    )


async def format_statistics(income):
    stats = ""
    for data in income:
        price, method = data
        method = "карта" if method == "card" else "готівка"
        stats += f"{price} {method} "
    return stats


@creator_statistic_router.callback_query(lambda c: c.data.startswith("creator_statistic_menu_"))
async def handler_creator_statistic(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, chat_data: ChatDataMiddleware):
    type_statistic = callback_query.data.split("_")[-1]
    await chat_data.set_chat_data(callback_query, 'type_statistic', type_statistic)

    if type_statistic == "gym":
        day_statistic = await format_statistics(await get_gym_income(session, "day"))
        month_statistic = await format_statistics(
            await get_gym_income(session, "month")
        )
        year_statistic = await format_statistics(await get_gym_income(session, "year"))
    elif type_statistic == "goods":
        day_statistic = await format_statistics(await get_goods_income(session, "day"))
        month_statistic = await format_statistics(
            await get_goods_income(session, "month")
        )
        year_statistic = await format_statistics(
            await get_goods_income(session, "year")
        )
    elif type_statistic == "client":
        telegram_id = callback_query.from_user.id

        day_statistic = await format_statistics(
            await orm_get_client_income(session, telegram_id, "day")
        )
        month_statistic = await format_statistics(
            await orm_get_client_income(session, telegram_id, "month")
        )
        year_statistic = await format_statistics(
            await orm_get_client_income(session, telegram_id, "year")
        )
    else:
        day_statistic = month_statistic = year_statistic = "Невідомий тип статистики"
    await callback_query.message.edit_text(
        text=f"Сьогодні: {day_statistic}\nМісячний: {month_statistic}\nРічний: {year_statistic}",
        reply_markup=await check_details_menu_button())
