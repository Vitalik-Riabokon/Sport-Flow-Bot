from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.reg_log_but import main_manu, start_button
from database.func.table_users import orm_get_telegram_id, orm_get_user_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware

menu_router = Router()


@menu_router.message(Command("menu"))
async def handler_send_main_menu(message: Message, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, message)
    telegram_id = message.from_user.id
    if telegram_id in await orm_get_telegram_id(session=session):
        user = await orm_get_user_by_telegram_id(
            session=session, telegram_id=telegram_id)
        event = await message.answer(
            "Натисніть на кнопку для повернення у головне меню⤵️",
            reply_markup=await main_manu(user.status))
        await logger.add_message(event)
    else:
        event = await message.answer(
            "Будь ласка, зареєструйтесь або увійдіть в акаунт, щоб отримати доступ до головного меню.",
            reply_markup=start_button)
        await logger.add_message(event)
