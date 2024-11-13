from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import get_category_buttons
from buttons.creator_menu_button import next_redact_button
from database.func.table_products import orm_get_all_category, orm_status_product_column, orm_update_category
from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

add_category_router = Router()


@add_category_router.callback_query(F.data == "add_new_category")
async def handler_add_new_category(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    await state.set_state(Redact.category_name)
    category = []
    await chat_data.set_chat_data(callback_query, 'category', category)
    category_switch = True
    await chat_data.set_chat_data(callback_query, 'category_switch', chat_data)
    event = await callback_query.message.answer(
        text="Введдіть назву категорії:",
        reply_markup=await next_redact_button(
            category=category, category_switch=category_switch))
    await logger.add_message(event)


@add_category_router.message(Redact.category_name)
async def handler_fsm_category_name(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, message)
    category_switch = await chat_data.get_chat_data(message, 'category_switch')
    change_category = await chat_data.get_chat_data(message, 'change_category')
    if message.text.isdigit():
        event = await message.answer(text="Введіть коректні дані!")
    else:
        if message.text.capitalize() in await orm_get_all_category(session, False):
            await orm_status_product_column(
                session=session,
                column="category",
                status_product=None,
                column_value=message.text.capitalize(),
            )
            event = await message.answer(
                text="Ця категорія існує у базі!\nКатегорія з товарами розблоковані",
                reply_markup=await get_category_buttons(session, message.from_user.id),
            )
        elif change_category:
            data = await state.get_data()
            await orm_update_category(
                session=session,
                old_category=data["old_category_name"],
                new_category=message.text.capitalize(),
            )
            event = await message.answer(
                "Назва змінена\nОберіть категорію:",
                reply_markup=await get_category_buttons(session, message.from_user.id),
            )
            await chat_data.set_chat_data(message, 'change_category', False)

        else:
            await state.update_data(category_name=message.text.capitalize())
            event = await message.answer(
                text="Введдіть назву для нового продукту:",
                reply_markup=await next_redact_button(
                    category=message.text.capitalize(), category_switch=category_switch
                ),
            )
            await state.set_state(Redact.goods_name)
        await logger.add_message(event)
    await logger.add_message(event)
