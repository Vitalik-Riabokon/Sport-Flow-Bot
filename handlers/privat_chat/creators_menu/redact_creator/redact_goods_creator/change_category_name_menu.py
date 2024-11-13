from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

change_category_name_router = Router()


@change_category_name_router.callback_query(F.data.startswith("change_category_name_"))
async def handler_change_category_name(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)
    old_category = callback_query.data.split("_")[-1]
    await state.update_data(old_category_name=old_category)
    await state.set_state(Redact.category_name)
    await chat_data.set_chat_data(callback_query, 'change_category', True)
    event = await callback_query.message.answer(
        text="Введіть нову назву категорії",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text="Назад🔙",
                callback_data=f"category_{old_category}")]]))
    await logger.add_message(event)
