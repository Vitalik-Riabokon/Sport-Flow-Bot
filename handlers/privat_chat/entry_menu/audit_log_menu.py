from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.reg_log_but import start_button
from database.func.table_users import orm_get_user_by_telegram_id, orm_update_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware

audit_log_menu_router = Router()


@audit_log_menu_router.callback_query(lambda c: c.data.startswith("confirm_login_"))
async def handler_confirm_login(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                                logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    new_telegram_id = int(callback_query.data.split("_")[-1])
    user_id = callback_query.from_user.id
    user = await orm_get_user_by_telegram_id(session, user_id)

    event = await callback_query.message.answer(
        text="Вхід підтверджено. Основний акаунт змінено\nУвійдіть в акаунт або зареєструйтесь",
        reply_markup=start_button)
    await logger.add_message(event)

    if user:
        await orm_update_telegram_id(session, new_telegram_id, user.user_id)
        event = await bot.send_message(
            new_telegram_id, "Вхід підтверджено✨ Ви успішно увійшли в акаунт\nНатисніть на /menu")
        await logger.add_message(event)
    else:
        await callback_query.answer("Помилка підтвердження входу.", show_alert=True)


@audit_log_menu_router.callback_query(lambda c: c.data.startswith("deny_login_"))
async def handler_deny_login(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                             logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    telegram_id = int(callback_query.data.split("_")[-1])
    await bot.send_message(
        telegram_id,
        "Запит відхилено😔\nПройдіть реєстрацію або увійдіть в акаунт:",
        reply_markup=start_button)
