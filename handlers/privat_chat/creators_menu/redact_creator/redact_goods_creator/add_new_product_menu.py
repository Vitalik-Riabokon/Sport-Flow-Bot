from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from buttons.creator_menu_button import next_redact_button
from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

add_product_router = Router()


@add_product_router.callback_query(F.data.startswith("add_new_product_"))
async def handler_add_new_product(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)

    category = callback_query.data.split("_")[-1]
    await state.set_state(Redact.goods_name)
    await state.update_data(category_name=category)
    await chat_data.set_chat_data(callback_query, 'category_switch', True)
    category = await chat_data.get_chat_data(callback_query, 'category')
    category_switch = await chat_data.get_chat_data(callback_query, 'category_switch')
    event = await callback_query.message.answer(
        text="Введдіть назву продукта:",
        reply_markup=await next_redact_button(
            category=category, category_switch=category_switch))
    await logger.add_message(event)
