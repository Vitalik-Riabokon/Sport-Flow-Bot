from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import client_program_button
from database.func.table_users import orm_get_user_by_telegram_id
from middlewares.Safe_memory import ChatDataMiddleware

client_program_admin_router = Router()


@client_program_admin_router.callback_query(lambda c: c.data.startswith("client_program_"))
async def handler_client_program(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                                 chat_data: ChatDataMiddleware):
    user = await orm_get_user_by_telegram_id(session, callback_query.from_user.id)
    if user.status != 'client':
        trainer_telegram_id = callback_query.from_user.id
        await chat_data.set_chat_data(callback_query, 'trainer_telegram_id', trainer_telegram_id)
        client_telegram_id = int(callback_query.data.split("_")[-1])
        await chat_data.set_chat_data(callback_query, 'client_telegram_id', client_telegram_id)
    else:
        trainer_telegram_id = int(callback_query.data.split("_")[-1])
        await chat_data.set_chat_data(callback_query, 'trainer_telegram_id', trainer_telegram_id)
        client_telegram_id = callback_query.from_user.id
        await chat_data.set_chat_data(callback_query, 'client_telegram_id', client_telegram_id)
    await callback_query.message.edit_text(
        "Оберіть місяць:",
        reply_markup=await client_program_button(session, callback_query.from_user.id, client_telegram_id),
    )
