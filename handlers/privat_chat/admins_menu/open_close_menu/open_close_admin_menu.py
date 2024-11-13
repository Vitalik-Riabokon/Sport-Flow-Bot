from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import admin_menu_button
from database.func.table_shifts import orm_get_active_shift, orm_open_shift, orm_close_shift
from database.func.table_users import orm_get_user_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware

open_close_admin_router = Router()


@open_close_admin_router.callback_query(F.data == "open_work")
async def open_work(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                    logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)

    telegram_id = callback_query.from_user.id
    active_shift = await orm_get_active_shift(session)

    if active_shift:
        await callback_query.message.answer(
            f"Зміна вже відкрита іншим працівником - {active_shift.first_name}",
            reply_markup=await admin_menu_button(session, callback_query.from_user.id))
    else:
        await orm_open_shift(session, telegram_id)
        await callback_query.answer(f"Зміна відкрита.", show_alert=True)
        event = await callback_query.message.answer(
            "Ваша зміна відкрита✅ Оберіть дію:",
            reply_markup=await admin_menu_button(session, callback_query.from_user.id))
        await logger.add_message(event)


@open_close_admin_router.callback_query(F.data == "close_work")
async def close_work(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                     logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    active_shift = await orm_get_active_shift(session)
    user = await orm_get_user_by_telegram_id(session, callback_query.from_user.id)
    if active_shift and user.user_id == active_shift.user_id:
        await orm_close_shift(session, active_shift.id)
        await callback_query.answer("Зміна закрита.", show_alert=True)
        event = await callback_query.message.answer(
            "Ваша зміна закрита🚫 Оберіть дію:",
            reply_markup=await admin_menu_button(session, callback_query.from_user.id),
        )
        await logger.add_message(event)

    else:
        await callback_query.answer(
            "У вас немає активної зміни для закриття.", show_alert=True
        )
