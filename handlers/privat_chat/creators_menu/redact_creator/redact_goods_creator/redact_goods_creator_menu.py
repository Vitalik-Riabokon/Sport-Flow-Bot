import re

from aiogram import F, Router, Bot
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import get_product_buttons
from buttons.creator_menu_button import next_redact_button
from database.func.table_products import orm_get_product_name_by_category, orm_status_product_column, \
    orm_update_product, orm_add_product
from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

redact_goods_creator_router = Router()


@redact_goods_creator_router.callback_query(F.data == "next_redact")
async def handler_next_redact(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)
    state_now = await state.get_state()
    category = await chat_data.get_chat_data(callback_query, 'category')
    if state_now.split(":")[-1] == "goods_name":
        await chat_data.set_chat_data(callback_query, 'category_switch', False)
        await state.set_state(Redact.goods_price)
        event = await callback_query.message.answer(
            "Введіть нову ціну для товару:",
            reply_markup=await next_redact_button(category=category))

    elif state_now.split(":")[-1] == "goods_price":
        await state.set_state(Redact.goods_description)
        event = await callback_query.message.answer(
            "Введіть новий опис товару:",
            reply_markup=await next_redact_button(category=category),
        )
    elif state_now.split(":")[-1] == "goods_description":
        await state.set_state(Redact.goods_photo)

        event = await callback_query.message.answer(
            "Добавте нову фотографію:",
            reply_markup=await next_redact_button(category=category),
        )
    else:

        event = await callback_query.message.answer(
            "Зміни пройшли успішно!",
            reply_markup=await get_product_buttons(session,
                                                   category,
                                                   telegram_id=callback_query.from_user.id))
    await logger.add_message(event)


@redact_goods_creator_router.message(Redact.goods_name)
async def handler_goods_name(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, message)
    category = await chat_data.get_chat_data(message, 'category')
    category_switch = await chat_data.get_chat_data(message, 'category_switch')
    product = await chat_data.get_chat_data(message, 'product')
    if message.text.isdigit():
        event = await message.answer(
            text="Введіть коректні дані")
    elif len(message.text.encode('utf-8')) > 48:
        event = await message.answer(
            text="Обмеженян розміру кнопки!\nЗменшіть розмір тексту!")
    else:
        if category and message.text.capitalize() in await orm_get_product_name_by_category(session,
                                                                                            category,
                                                                                            bloc=True):
            await orm_status_product_column(
                session=session,
                column="product_name",
                status_product=None,
                column_value=message.text.capitalize())
            event = await message.answer(
                text="Даний продукт вже існує у базі!\nПродукт був розблокований",
                reply_markup=await get_product_buttons(session,
                                                       category, telegram_id=message.from_user.id))
        elif category and message.text.capitalize() in await orm_get_product_name_by_category(session,
                                                                                              category):
            event = await message.answer(
                text="Даний продукт вже існує у базі!",
                reply_markup=await get_product_buttons(session,
                                                       category, telegram_id=message.from_user.id))
        else:
            await state.update_data(goods_name=message.text.capitalize())

            if not category_switch:
                await orm_update_product(
                    session, product, update_type=message.text.capitalize(), update_name="product_name"
                )
            await state.set_state(Redact.goods_price)
            event = await message.answer(
                "Введіть нову ціну для товару:",
                reply_markup=await next_redact_button(
                    category=category, category_switch=category_switch
                ))
        await logger.add_message(event)
    await logger.add_message(event)


@redact_goods_creator_router.message(Redact.goods_price)
async def handler_goods_price(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, message)
    category_switch = await chat_data.get_chat_data(message, 'category_switch')
    product = await chat_data.get_chat_data(message, 'product')
    price_pattern = r'^\d+(\.\d{1,2})?$'
    if not re.match(price_pattern, message.text):
        event = await message.answer(
            text="Будь ласка, введіть коректну ціну (ціле число або число з двома знаками після коми).")
    else:
        await state.update_data(goods_price=int(message.text))
        data = await state.get_data()
        if not category_switch:
            await orm_update_product(
                session, product, update_type=float(message.text), update_name="price"
            )
        else:
            await orm_add_product(
                session=session,
                product_name=data["goods_name"],
                price=data["goods_price"],
                category=data["category_name"]
            )
            await chat_data.set_chat_data(message, 'category', data["category_name"])
        category = await chat_data.get_chat_data(message, 'category')
        await state.set_state(Redact.goods_description)
        event = await message.answer(
            "Введіть новий опис товару:",
            reply_markup=await next_redact_button(category=category))
    await logger.add_message(event)


@redact_goods_creator_router.message(Redact.goods_description)
async def handler_goods_description(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, message)
    category_switch = await chat_data.get_chat_data(message, 'category_switch')
    product = await chat_data.get_chat_data(message, 'product')
    if not category_switch:
        await orm_update_product(
            session, product, update_type=message.text, update_name="description"
        )
    else:
        data = await state.get_data()
        await orm_update_product(
            session,
            data["goods_name"],
            update_type=message.text,
            update_name="description",
        )
        await chat_data.set_chat_data(message, 'category', data["category_name"])
    category = await chat_data.get_chat_data(message, 'category')
    await state.set_state(Redact.goods_photo)
    event = await message.answer(
        "Добавте нову фотографію:",
        reply_markup=await next_redact_button(category=category),
    )
    await logger.add_message(event)


@redact_goods_creator_router.message(Redact.goods_photo)
async def handler_goods_photo(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, message)
    category_switch = await chat_data.get_chat_data(message, 'category_switch')
    product = await chat_data.get_chat_data(message, 'product')
    if message.content_type != ContentType.PHOTO:
        event = await message.answer("Надішліть будь ласка фотографію")

    else:

        if not category_switch:
            await orm_update_product(
                session,
                product,
                update_type=message.photo[-1].file_id,
                update_name="photo",
            )
        else:
            data = await state.get_data()
            await orm_update_product(
                session,
                data["goods_name"],
                update_type=message.photo[-1].file_id,
                update_name="photo",
            )
            await chat_data.set_chat_data(message, 'category', data["category_name"])

        category = await chat_data.get_chat_data(message, 'category')
        await state.clear()
        event = await message.answer(
            "Зміни пройшли успішно!",
            reply_markup=await get_product_buttons(session,
                                                   category, telegram_id=message.from_user.id
                                                   ))
    await logger.add_message(event)
