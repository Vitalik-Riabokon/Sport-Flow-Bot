from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (CallbackQuery)
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import (client_menu_button)
from database.func.table_users import (orm_get_name)
from middlewares.DelMessages import MessageLoggingMiddleware

client_router = Router()


@client_router.callback_query(F.data == "menu_client")
async def client_menu(callback_query: CallbackQuery, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    full_name = await orm_get_name(session, callback_query.from_user.id)
    if full_name:
        first_name, last_name = full_name
    else:
        first_name, last_name = "", ""
    event = await callback_query.message.answer(
        f"{first_name} {last_name}🖐️\nЩо бажаєте?",
        reply_markup=await client_menu_button(session, callback_query.from_user.id))
    await logger.add_message(event)
