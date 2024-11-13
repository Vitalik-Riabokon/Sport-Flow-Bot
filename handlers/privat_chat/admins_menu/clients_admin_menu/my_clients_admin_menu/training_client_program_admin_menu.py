from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import month_button
from middlewares.Safe_memory import ChatDataMiddleware

training_client_program_admin_router = Router()


@training_client_program_admin_router.callback_query(lambda c: c.data.startswith("training_client_program_"))
async def program_menu(callback_query: CallbackQuery, bot: Bot, session: AsyncSession, chat_data: ChatDataMiddleware):
    client_telegram_id = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'client_telegram_id', client_telegram_id)
    await callback_query.message.edit_text(
        "Оберіть місяць:",
        reply_markup=await month_button(session, client_telegram_id))
