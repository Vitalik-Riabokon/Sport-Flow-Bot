from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_payments import orm_get_expiration_date
from database.func.table_products import orm_get_data_by_product_id
from database.func.table_trainer_clients import orm_get_client_data
from database.func.table_training_sessions import orm_get_session_date_visiting, orm_get_count_visiting
from database.func.table_users import orm_get_user_id_by_telegram_id

client_members_admin_router = Router()


@client_members_admin_router.callback_query(lambda c: c.data.startswith("client_memberships_"))
async def client_statistics(callback_query: CallbackQuery, session: AsyncSession):
    client_telegram_id = int(callback_query.data.split("_")[-1])
    user_id = await orm_get_user_id_by_telegram_id(session=session, telegram_id=client_telegram_id)
    date_time = await orm_get_expiration_date(session, user_id)

    for date_client in await orm_get_client_data(session, client_telegram_id):
        (_, _, _, first_name, last_name, phone_nuber, price_per_session, start_date, end_data) = date_client
    date_visiting = await orm_get_session_date_visiting(session, user_id)

    if date_time:
        product_id, payment_date, expiration_date = date_time
        product_name, price = await orm_get_data_by_product_id(session, product_id)
        data = await orm_get_count_visiting(session, user_id)
        if data:
            count_visiting, sum_price = data
        else:
            count_visiting, sum_price = "Не має даних", "Не має даних"
        await callback_query.message.edit_text(
            text=f"Ініціали: {first_name} {last_name}\n"
                 f"Номер телефону: {phone_nuber}\n"
                 f"Початок: {payment_date}\nКінець: {expiration_date}\n"
                 f"Абонимент: {product_name} - {price}\n\n"
                 f"Ціна сеансу: {price_per_session}\n"
                 f"Дата початку тренування з тренером: {start_date}\n"
                 f"Місячна кількість відвідування: {count_visiting}\n"
                 f"Місячний Дохід: {sum_price}\n\n"
                 f"Дні відвідування:\n{date_visiting}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(
                    text="Назад🔙",
                    callback_data=f"client_data_{client_telegram_id}")]]))
    else:
        data = await orm_get_count_visiting(session, user_id)
        if data:
            count_visiting, sum_price = data
            if count_visiting == 0 or sum_price is None:
                count_visiting, sum_price = "Не має даних", "Не має даних"
        else:
            count_visiting, sum_price = "Не має даних", "Не має даних"
        await callback_query.message.edit_text(
            "Користувач не має абонименту\n"
            f"Місячна кількість відвідування: {count_visiting}\n"
            f"Місячний дохід: {sum_price}\n\n"
            f"Дні відвідування:\n{date_visiting}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Назад🔙",
                        callback_data=f"client_data_{client_telegram_id}",
                    )]]))
