from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import type_buy_button
from database.func.table_payments import orm_get_expiration_date
from database.func.table_products import orm_get_product_price, orm_get_product_description
from database.func.table_users import orm_get_user_id_by_telegram_id
from middlewares.Safe_memory import ChatDataMiddleware

one_time_training_client_router = Router()


@one_time_training_client_router.callback_query(F.data == "one_time_training")
async def handler_one_training(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                               chat_data: ChatDataMiddleware):
    await chat_data.set_chat_data(callback_query, 'product_name', "Одноразове")
    telegram_id = callback_query.from_user.id
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=telegram_id
    )
    date_time = await orm_get_expiration_date(session, user_id)
    if date_time:
        await callback_query.message.delete()
        await callback_query.message.answer(
            f"Вам не потібні разові тренування так як у вас є абонимент",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад🔙", callback_data="menu_client")]
                ]
            ),
        )

    else:
        product_price = await orm_get_product_price(session, "Одноразове")
        product_description = await orm_get_product_description(session, "Одноразове")
        await callback_query.message.edit_text(
            f"Опис: {product_description}\nЦіна: {product_price}",
            reply_markup=await type_buy_button(
                callbackcash="type_cash",
                callbackcard="type_card",
                callback="menu_client",
            ),
        )

    await callback_query.answer("Розділ Разових тренувань")
