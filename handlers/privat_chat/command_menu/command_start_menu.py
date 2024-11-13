from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from buttons.reg_log_but import start_button
from filters.chat_types import ChatTypeFilter
from middlewares.DelMessages import MessageLoggingMiddleware

start_router = Router()
start_router.message.filter(ChatTypeFilter(["private"]))


@start_router.message(CommandStart())
async def start(message: Message, bot: Bot, logger: MessageLoggingMiddleware):
    await message.delete()
    await logger.del_all_messages(bot, message)
    event = await message.answer(text="Вас вітає команда Sport Flow🖐️", reply_markup=start_button)
    await logger.add_message(event)