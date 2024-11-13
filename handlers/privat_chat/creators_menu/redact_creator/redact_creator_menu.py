from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery

from buttons.creator_menu_button import creator_redact_menu_button
from middlewares.DelMessages import MessageLoggingMiddleware

redact_creator_router = Router()


@redact_creator_router.callback_query(F.data == "redact")
async def handler_redact(callback_query: CallbackQuery, bot: Bot,
                         logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    event = await callback_query.message.answer(
        f"Налаштовуйте ціни товарів та абониментів: ",
        reply_markup=await creator_redact_menu_button())
    await logger.add_message(event)
