from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from buttons.admin_buttons import clients_button
from middlewares.DelMessages import MessageLoggingMiddleware

client_admin_router = Router()


@client_admin_router.callback_query(F.data == "clients")
async def choose_client(callback_query: CallbackQuery,
                        logger: MessageLoggingMiddleware, bot: Bot):
    await logger.del_all_messages(bot, callback_query)
    await callback_query.message.answer(
        f"Деталі над якими клієнтами бажаєте отримати:",
        reply_markup=await clients_button())
    await callback_query.answer("Розділ Клієнтів")
