from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_payments import orm_get_person_gym
from database.func.table_training_sessions import orm_get_sessions_today, orm_get_client_income
from database.func.table_users import orm_get_user_id_by_telegram_id, orm_get_user_by_telegram_id
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.statistic_creator_menu import format_statistics, \
    get_goods_income, get_gym_income
from middlewares.Safe_memory import ChatDataMiddleware

detail_day_router = Router()


@detail_day_router.callback_query(F.data.startswith("creator_day_"))
async def handler_creator_day(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
        chat_data: ChatDataMiddleware
):
    creator_month = await chat_data.get_chat_data(callback_query, 'creator_month')
    type_statistic = await chat_data.get_chat_data(callback_query, 'type_statistic')
    creator_day = int(callback_query.data.split("_")[-1])
    trainer_telegram_id = callback_query.from_user.id
    trainer_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=trainer_telegram_id)
    session_data = await orm_get_sessions_today(
        session, trainer_id, month_number=creator_month, day_number=creator_day)
    text = ""
    user = await orm_get_user_by_telegram_id(session, trainer_telegram_id)
    if type_statistic == "gym":
        day_statistic = await format_statistics(
            await get_gym_income(
                session, "day", month_number=creator_month, day_number=creator_day
            )
        )

        statistics = await orm_get_person_gym(
            session=session, month_number=creator_month, day_number=creator_day
        )
        print('💪', statistics)
        if statistics:
            for statistic in statistics:
                client_first_name, client_last_name, price, payment_method = statistic
                price_payment_method = await format_statistics(
                    income=[(price, payment_method)]
                )
                text += f"\n{client_first_name} {client_last_name}: {price_payment_method}\n"
    elif type_statistic == "goods":
        day_statistic = await format_statistics(
            await get_goods_income(
                session, "day", month_number=creator_month, day_number=creator_day
            )
        )
        statistics = await orm_get_person_gym(
            session=session,
            month_number=creator_month,
            day_number=creator_day,
            switch=True,
        )
        if statistics:
            for statistic in statistics:
                (
                    client_first_name,
                    client_last_name,
                    product_name,
                    price,
                    payment_method,
                ) = statistic
                price_payment_method = await format_statistics(
                    income=[(price, payment_method)]
                )
                text += f"\n{client_first_name} {client_last_name}: {product_name} - {price_payment_method}\n"

    elif type_statistic == "client":
        telegram_id = callback_query.from_user.id
        day_statistic = await format_statistics(
            await orm_get_client_income(
                session,
                telegram_id,
                "day",
                month_number=creator_month,
                day_number=creator_day,
            )
        )

        for session in session_data:
            client_first_name, client_last_name, phone_number, payment_method, price = (
                session
            )
            statistic = await format_statistics(income=[(price, payment_method)])
            text += f"\n{client_first_name} {client_last_name} {phone_number}: {statistic}\n"

    else:
        day_statistic = "Дані не отримані"
    await callback_query.message.edit_text(
        text=f"Тренер: {user.first_name} {user.last_name}\nДохід для цього дня становить: {day_statistic}\n"
             + text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Назад🔙",
                    callback_data=f"creator_month_{creator_month}")]]))
