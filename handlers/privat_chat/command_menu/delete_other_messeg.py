from aiogram import Router, F, Bot
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

delete_message_router = Router()
delete_message_router.message.filter(ChatTypeFilter(["private"]))


@delete_message_router.message(~F.text.startswith('/'), default_state)
async def handle_all_messages(message: Message, logger: MessageLoggingMiddleware, bot: Bot,
                              chat_data: ChatDataMiddleware):
    # user = await orm_get_user_by_telegram_id(session=session, telegram_id=message.from_user.id)
    await logger.print_all_messages()
    await message.delete()
    await chat_data.print_all_chat_data()
    # event = await message.answer("Перейдіть у головне меню✨", reply_markup=await main_manu(user.status))
    # await logger.add_message(event)
