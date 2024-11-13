from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import verification_client, type_buy_button, client_menu_button
from database.func.table_trainer_clients import orm_get_client_data
from database.func.table_training_sessions import orm_add_session
from database.func.table_users import orm_get_name, orm_get_user_id_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware
from mono_data.transaction_verification import get_last_incoming_transaction_today

session_client_router = Router()


@session_client_router.callback_query(lambda c: c.data.startswith("payment_training_"))
async def handler_payment_training(callback_query: CallbackQuery, bot: Bot,
                                   logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    trainer_telegram_id = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'trainer_telegram_id', trainer_telegram_id)
    await logger.del_all_messages(bot, callback_query)

    event = await callback_query.message.answer(
        f"Оберіть операцію:",
        reply_markup=await type_buy_button(
            callbackcash="session_type_cash",
            callbackcard="session_type_card",
            callback="training",
        ))

    await logger.add_message(event)


@session_client_router.callback_query(lambda c: c.data.startswith("training_finish_payment_"))
async def handler_training_finish_payment(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    await callback_query.message.delete()
    client_telegram_id = int(callback_query.data.split("_")[-1])
    trainer_telegram_id = await chat_data.get_chat_data(client_telegram_id, 'trainer_telegram_id')
    payment_method = await chat_data.get_chat_data(client_telegram_id, 'payment_method')
    client_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id
    )
    trainer_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=trainer_telegram_id
    )
    for client_data in await orm_get_client_data(session, client_telegram_id):
        price_per_session = client_data[-3]

    await orm_add_session(
        session=session,
        client_id=client_id,
        trainer_id=trainer_id,
        price_session=price_per_session,
        payment_method=payment_method,
    )
    event = await bot.send_message(
        client_telegram_id,
        f"Оплата успішна:",
        reply_markup=await client_menu_button(session, client_telegram_id),
    )
    await logger.add_message(event)


@session_client_router.callback_query(lambda c: c.data.startswith("session_type_"))
async def session_cash(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                       logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):

    await callback_query.answer(
        "Дякую за вибір! Очікуйте на підтвердження",
        show_alert=True)
    await callback_query.message.delete()

    trainer_telegram_id = await chat_data.get_chat_data(callback_query, 'trainer_telegram_id')

    payment_method = callback_query.data.split("_")[-1]
    await chat_data.set_chat_data(callback_query, 'payment_method', payment_method)
    if payment_method == "card":
        payment_method_uk = "карта"
    else:
        payment_method_uk = "готівка"
    client_telegram_id = callback_query.from_user.id
    first_name, last_name = await orm_get_name(session, client_telegram_id)

    if payment_method == 'card':
        startswith_middle = 'transaction_session_update_'
        text = await get_last_incoming_transaction_today()
    else:
        startswith_middle = None
        text = ''
    event = await bot.send_message(
        trainer_telegram_id,
        text=f"Переконайтесь, що клієнтом {first_name} {last_name} оплачено тренувальний сеанс.\n"
             f"Вид оплати: {payment_method_uk}\n\n" + text,
        reply_markup=await verification_client(
            startswith_yes="training_finish_payment_",
            startswith_not="negative_",
            startswith_middle=startswith_middle,
            telegram_id=client_telegram_id,
        ))
    await logger.add_message(event)


@session_client_router.callback_query(lambda c: c.data.startswith("transaction_session_update_"))
async def handler_transaction_session_update(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                                             logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)

    client_telegram_id = int(callback_query.data.split("_")[-1])
    first_name, last_name = await orm_get_name(session, client_telegram_id)

    text = await get_last_incoming_transaction_today()

    event = await bot.send_message(
        callback_query.message.chat.id,
        text=f"Переконайтесь, що клієнтом {first_name} {last_name} оплачено тренувальний сеанс.\n"
             f"Вид оплати: карта\n\n" + text,
        reply_markup=await verification_client(
            startswith_yes="training_finish_payment_",
            startswith_not="negative_",
            startswith_middle='transaction_session_update_',
            telegram_id=client_telegram_id,
        ))
    await logger.add_message(event)
