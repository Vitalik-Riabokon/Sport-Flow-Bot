from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import day_buttons
from database.func.table_training_sessions import orm_get_client_income
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.statistic_creator_menu import format_statistics, \
    get_goods_income, get_gym_income
from middlewares.Safe_memory import ChatDataMiddleware

detail_month_router = Router()


@detail_month_router.callback_query(F.data.startswith("creator_month_"))
async def handler_creator_month(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, chat_data: ChatDataMiddleware
):
    type_statistic = await chat_data.get_chat_data(callback_query, 'type_statistic')
    telegram_id = callback_query.from_user.id
    creator_month = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'creator_month', creator_month)
    if type_statistic == "gym":
        month_statistic = await format_statistics(
            await get_gym_income(session, "month", month_number=creator_month)
        )
    elif type_statistic == "goods":
        month_statistic = await format_statistics(
            await get_goods_income(session, "month", month_number=creator_month)
        )
    elif type_statistic == "client":

        month_statistic = await format_statistics(
            await orm_get_client_income(
                session, telegram_id, "month", month_number=creator_month
            )
        )
    else:
        month_statistic = "Дані не отримані"

    await callback_query.message.edit_text(
        text=f"Дохід цього місяця становить: {month_statistic}",
        reply_markup=await day_buttons(session=session, type_statistic=type_statistic, telegram_id=telegram_id,
                                       month=creator_month, start_with="creator_", switch=True
                                       ),
    )
