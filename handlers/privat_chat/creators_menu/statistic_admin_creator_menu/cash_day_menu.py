from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_training_sessions import orm_get_sessions_today
from database.func.table_users import orm_get_user_id_by_telegram_id
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.statistic_creator_menu import format_statistics

cash_day_router = Router()


@cash_day_router.callback_query(F.data == "cash_day")
async def handler_cash_day(callback_query: CallbackQuery, session: AsyncSession):
    trainer_telegram_id = callback_query.from_user.id
    trainer_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=trainer_telegram_id
    )
    session_data = await orm_get_sessions_today(session, trainer_id)
    text = ""
    sum_price = 0
    for session in session_data:
        client_first_name, client_last_name, phone_number, payment_method, price = (
            session
        )
        sum_price += price
        statistic = await format_statistics(income=[(price, payment_method)])
        text += f"\n{client_first_name} {client_last_name} {phone_number}\nДохід: {statistic}\n"
    # user = await orm_get_user_by_telegram_id(session=session, telegram_id=trainer_telegram_id)
    await callback_query.message.edit_text(
        text=f"Дохід від ваших клієнтів: {sum_price}\n" + text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад🔙", callback_data=f"my_clients")]
            ]
        ),
    )
