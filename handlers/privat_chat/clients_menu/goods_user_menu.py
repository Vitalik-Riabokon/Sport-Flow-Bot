from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery)
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import (get_category_buttons, get_product_buttons, get_details)
from buttons.creator_menu_button import next_redact_button
from database.func.table_users import (orm_get_user_by_telegram_id)
from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

goods_client_router = Router()


@goods_client_router.callback_query(lambda c: c.data.startswith("goods") or c.data == "goods")
async def handler_gym_goods(
        callback_query: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)

    switch_creator = callback_query.data.split("_")[-1]
    if switch_creator == 'switch':
        switch_creator = False
    else:
        switch_creator = True

    await chat_data.set_chat_data(callback_query, 'switch_creator', switch_creator)
    category_switch = False
    await chat_data.set_chat_data(callback_query, 'category_switch', category_switch)

    await state.clear()
    await callback_query.message.answer(
        "Оберіть категорію:",
        reply_markup=await get_category_buttons(session, callback_query.from_user.id,
                                                switch_creator=switch_creator),
    )
    await callback_query.answer("Розділ Товарів")


@goods_client_router.callback_query(lambda c: c.data.startswith("category_"))
async def handler_show_category(
        callback_query: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)
    category = callback_query.data.split("_")[1]
    await chat_data.set_chat_data(callback_query, 'category', category)
    switch_creator = await chat_data.get_chat_data(callback_query, 'switch_creator')
    await state.clear()
    await callback_query.answer(category)
    event = await callback_query.message.answer(
        f"Товари у категорії {category}:",
        reply_markup=await get_product_buttons(session=session,
                                               category=category,
                                               telegram_id=callback_query.from_user.id,
                                               switch_creator=switch_creator))
    await logger.add_message(event)


@goods_client_router.callback_query(lambda c: c.data.startswith("page_"))
async def handler_paginate_category(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                                    chat_data: ChatDataMiddleware):
    _, category, page = callback_query.data.split("_")
    page = int(page)
    switch_creator = await chat_data.get_chat_data(callback_query, 'switch_creator')

    if category == "category":
        await callback_query.message.edit_text(
            f"Оберіть категорію:",
            reply_markup=await get_category_buttons(
                session, telegram_id=callback_query.from_user.id, page=page
            ),
        )
    else:
        await callback_query.message.edit_text(
            f"Товари у категорії {category}:",
            reply_markup=await get_product_buttons(session,
                                                   category, page,
                                                   telegram_id=callback_query.from_user.id,
                                                   switch_creator=switch_creator))


@goods_client_router.callback_query(lambda c: c.data.startswith("few_"))
async def handler_few_product(
        callback_query: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware):
    pass

@goods_client_router.callback_query(lambda c: c.data.startswith("product_"))
async def handler_show_product(
        callback_query: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)
    product = callback_query.data.split("_")[1]
    await chat_data.set_chat_data(callback_query, 'product', product)
    print('❗product', product)
    category = await chat_data.get_chat_data(callback_query, 'category')
    switch_creator = await chat_data.get_chat_data(callback_query, 'switch_creator')

    user = await orm_get_user_by_telegram_id(session, callback_query.from_user.id)
    if user.status == "creator" and switch_creator:
        event = await callback_query.message.answer(
            f"Введіть нову назву для товару {product}:",
            reply_markup=await next_redact_button(
                category=category, product=product, del_switch=True
            ),
        )

        await state.set_state(Redact.goods_name)
    else:
        text, image, keyboard = await get_details(session, product)
        if image is None:
            event = await callback_query.message.answer(text=text, reply_markup=keyboard)
        else:
            event = await callback_query.message.answer_photo(
                photo=image, caption=text, reply_markup=keyboard
            )
        await callback_query.answer(product)
    await logger.add_message(event)


@goods_client_router.callback_query(lambda c: c.data.startswith("back_to_category_"))
async def handler_back_to_category(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    await state.clear()
    category = callback_query.data.split("_")[-1]
    switch_creator = await chat_data.get_chat_data(callback_query, 'switch_creator')

    event = await callback_query.message.answer(
        f"Товари у категорії {category}:",
        reply_markup=await get_product_buttons(session,
                                               category,
                                               telegram_id=callback_query.from_user.id,
                                               switch_creator=switch_creator))
    await logger.add_message(event)


@goods_client_router.callback_query(lambda c: c.data == "back_to_categories")
async def handler_back_to_categories(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                                     logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)
    switch_creator = await chat_data.get_chat_data(callback_query, 'switch_creator')
    event = await callback_query.message.answer(
        "Оберіть категорію:",
        reply_markup=await get_category_buttons(session, callback_query.from_user.id,
                                                switch_creator=switch_creator))
    await logger.add_message(event)
