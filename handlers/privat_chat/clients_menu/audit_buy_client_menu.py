from datetime import datetime

from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import admin_menu_button
from buttons.client_menu_button import type_buy_button, verification_client, client_menu_button
from database.func.table_payments import orm_add_payment
from database.func.table_products import orm_get_product_id_category
from database.func.table_shifts import orm_get_active_shift
from database.func.table_trainers import orm_get_trainer_id_by_user_id
from database.func.table_users import orm_get_user_id_by_telegram_id, orm_get_name, orm_get_user_by_telegram_id, \
    orm_get_trainer_full_name
from handlers.privat_chat.admins_menu.admin_menu import admin_menu
from handlers.privat_chat.clients_menu.client_menu import client_menu
from handlers.privat_chat.creators_menu.creator_menu import creator_menu
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware
from mono_data.transaction_verification import get_last_incoming_transaction_today

audit_buy_client_router = Router()


@audit_buy_client_router.callback_query(lambda c: c.data.startswith("buy_"))
async def handler_buy_membership(callback_query: CallbackQuery,
                                 logger: MessageLoggingMiddleware, bot: Bot, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)

    product_name = callback_query.data.split("_")[-1]
    await chat_data.set_chat_data(callback_query, 'product_name', product_name)

    category = await chat_data.get_chat_data(callback_query, 'category')
    if category:
        event = await callback_query.message.answer(
            text="Оберіть вид оплати:",
            reply_markup=await type_buy_button(
                callbackcash="type_cash",
                callbackcard="type_card",
                callback=f"product_{product_name}",
            ))
        await logger.add_message(event)
    else:
        event = await callback_query.message.answer(
            text="Оберіть вид оплати:",
            reply_markup=await type_buy_button(
                callbackcash="type_cash",
                callbackcard="type_card",
                callback="memberships",
            ),
        )
        await logger.add_message(event)

    await callback_query.answer("Дякую за вибір")


@audit_buy_client_router.callback_query(lambda c: c.data.startswith("type_"))
async def handler_type_buy(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                           logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):

    type_method = callback_query.data.split("_")[-1]
    await chat_data.set_chat_data(callback_query, 'type_method', type_method)

    if callback_query.data.split("_")[-1] == "card":
        type_method = "карта"
    else:
        type_method = "готівка"

    active_shift = await orm_get_active_shift(session)

    client_telegram_id = callback_query.from_user.id

    await chat_data.set_chat_data(callback_query, 'client_telegram_id', client_telegram_id)

    first_name, last_name = await orm_get_name(session, client_telegram_id)
    if active_shift:
        await callback_query.answer(
            "Дякую за вибір! Очікуйте на підтвердження працівником на рецепшені",
            show_alert=True,
        )
        await logger.del_all_messages(bot, callback_query)

        try:
            await callback_query.message.delete()
        except Exception as e:
            pass
        if type_method == 'карта':
            startswith_middle = 'transaction_update_'
            text = await get_last_incoming_transaction_today()
        else:
            startswith_middle = None
            text = ''
        user = await orm_get_trainer_full_name(session, active_shift.user_id)
        product_name = await chat_data.get_chat_data(callback_query, "product_name")
        event = await bot.send_message(
            user.telegram_id,
            text=f"{first_name} {last_name} бажає отримати: {product_name}. Вид оплати: {type_method}\n\n" + text,
            reply_markup=await verification_client(
                startswith_yes="confirm_",
                startswith_not="negative_",
                telegram_id=client_telegram_id,
                startswith_middle=startswith_middle))
        await logger.add_message(event)

    else:
        await callback_query.answer(
            "На даний момент обслуговування не можливе! Зверніться до рецепшена",
            show_alert=True,
        )
        await logger.del_all_messages(bot, callback_query)

        user = await orm_get_user_by_telegram_id(session, callback_query.from_user.id)
        if "admin" in user.status:
            event = await admin_menu(callback_query, bot, session, logger)
        elif "creator" in user.status:
            event = await creator_menu(callback_query, bot, session, logger)
        else:
            event = await client_menu(callback_query, bot, session, logger)
        await logger.add_message(event)


@audit_buy_client_router.callback_query(lambda c: c.data.startswith("confirm_"))
async def handler_finish_payment(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    telegram_id = int(callback_query.data.split("_")[-1])
    product_name = await chat_data.get_chat_data(telegram_id, "product_name")
    client_telegram_id = await chat_data.get_chat_data(telegram_id, "client_telegram_id")

    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=telegram_id)
    payment_method = await chat_data.get_chat_data(telegram_id, 'type_method')
    product = await orm_get_product_id_category(session, product_name)
    expiration_date = datetime.now().date()

    if "membership" in product.category:
        expiration_date = datetime.now() + relativedelta(months=1)
    print('👉👉', user_id, product.product_id, payment_method, product.price, expiration_date)
    await orm_add_payment(
        session=session,
        user_id=user_id,
        product_id=product.product_id,
        payment_method=payment_method,
        price=product.price,
        expiration_date=expiration_date,
    )
    first_name, last_name = await orm_get_name(session, telegram_id)

    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id
    )
    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
    if trainer_id:
        event = await bot.send_message(
            telegram_id,
            f"{first_name} {last_name}🖐️\nОплата пройшла успішно!",
            reply_markup=await admin_menu_button(session, telegram_id),
        )
    else:
        event = await bot.send_message(
            telegram_id,
            f"{first_name} {last_name}🖐️\nОплата пройшла успішно!",
            reply_markup=await client_menu_button(session, telegram_id),
        )
    await logger.add_message(event)
    await chat_data.clear_chat_data(callback_query, ('product_name',))


@audit_buy_client_router.callback_query(lambda c: c.data.startswith("negative_"))
async def handler_negative_payment(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await chat_data.clear_chat_data(callback_query, ('first_name', 'last_name', 'number'))
    await callback_query.message.delete()
    telegram_id = int(callback_query.data.split("_")[-1])
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=telegram_id)
    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
    if trainer_id:
        event = await bot.send_message(
            telegram_id,
            text="Відмовлено😞",
            reply_markup=await admin_menu_button(session, telegram_id),
        )
    else:
        event = await bot.send_message(
            telegram_id,
            text="Відмовлено😞 Підійдіть на рецепшен",
            reply_markup=await client_menu_button(session, telegram_id),
        )
    await logger.add_message(event)
    await chat_data.clear_chat_data(callback_query, ('product_name',))
