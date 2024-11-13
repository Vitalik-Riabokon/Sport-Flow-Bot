from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_trainer_clients import orm_get_trainer_id
from database.func.table_trainers import orm_get_trainer_details
from database.func.table_users import orm_get_user_id_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware

schedule_router = Router()


@schedule_router.callback_query(F.data == "schedule")
async def handler_schedule(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                           logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=callback_query.from_user.id)
    trainer_id = await orm_get_trainer_id(session=session, client_id=user_id)
    text = ""
    if trainer_id is not None:
        data_trainer = await orm_get_trainer_details(session, trainer_id)
        text = (f"Тренер: {data_trainer[0]['first_name']} {data_trainer[0]['last_name']}\n"
                f"Контакти: {data_trainer[0]['phone_number']}")
    await callback_query.message.answer(
        "Графік роботи: Пн-Сб 9.00 - 21.00\nОбід: 13.00 - 14.00\n\n"
        "Василь - (068) 099 29 24\n"
        "Владислава - (096) 563 38 09\n\n" + text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад🔙", callback_data="menu_client")],
            ]
        ),
    )
