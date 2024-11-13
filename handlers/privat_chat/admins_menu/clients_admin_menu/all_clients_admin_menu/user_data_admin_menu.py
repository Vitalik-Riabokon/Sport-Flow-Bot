from aiogram import Router, Bot
from aiogram.types import CallbackQuery

from buttons.admin_buttons import training_client_details
from middlewares.DelMessages import MessageLoggingMiddleware

user_data_admin_router = Router()


@user_data_admin_router.callback_query(lambda c: c.data.startswith("user_data_"))
async def client_details(callback_query: CallbackQuery, bot: Bot, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    client_telegram_id = int(callback_query.data.split("_")[-1])
    event = await callback_query.message.answer(
        f"Оберіть операцію над клієнтом:",
        reply_markup=await training_client_details(client_telegram_id),
    )
    await logger.add_message(event)
