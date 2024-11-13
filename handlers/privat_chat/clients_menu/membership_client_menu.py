from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import buy_membership_button
from database.func.table_payments import orm_get_expiration_date
from database.func.table_products import orm_get_data_by_product_id, orm_get_product_price, orm_get_product_description
from database.func.table_users import orm_get_user_id_by_telegram_id, orm_get_name

membership_client_router = Router()


@membership_client_router.callback_query(F.data == "memberships")
async def handler_memberships(callback_query: CallbackQuery, session: AsyncSession):
    telegram_id = callback_query.from_user.id
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=telegram_id)

    date_time = await orm_get_expiration_date(session, user_id)

    if date_time:
        first_name, last_name = await orm_get_name(session, telegram_id)
        product_id, payment_date, expiration_date = date_time
        product_name, price = await orm_get_data_by_product_id(session, product_id)
        await callback_query.message.edit_text(
            text=f"{first_name} {last_name}\n"
                 f"{payment_date} - {expiration_date}\n"
                 f"Абонимент: {product_name}.\nЦіна: {price}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад🔙", callback_data="menu_client")]
                ]
            ),
        )

    else:
        product_price_s = await orm_get_product_price(session, "Стандарт")
        product_description_s = await orm_get_product_description(session, "Стандарт")
        product_price_b = await orm_get_product_price(session, "Безлім")
        product_description_b = await orm_get_product_description(session, "Безлім")
        await callback_query.message.edit_text(
            f"Опис: {product_description_s}.\nЦіна: {product_price_s}\n"
            f"Опис: {product_description_b}.\nЦіна: {product_price_b}",
            reply_markup=buy_membership_button,
        )
        await callback_query.answer("Розділ абониментів")