from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import training_client_details
from buttons.client_menu_button import client_menu_button
from database.func.table_trainer_clients import orm_get_client_data, orm_update_client, orm_update_price_per_session, \
    orm_add_trainer_clients
from database.func.table_users import orm_get_user_id_by_telegram_id
from handlers.privat_chat.clients_menu.trainer_client_menu import Price
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

coach_yes_admin_router = Router()


@coach_yes_admin_router.callback_query(lambda c: c.data.startswith("coach_yes_"))
async def choose_coach_yes(callback_query: CallbackQuery, state: FSMContext, bot: Bot,
                           logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await callback_query.message.delete()
    client_telegram_id = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'client_telegram_id', client_telegram_id)
    await state.set_state(Price.price_session)
    event = await callback_query.message.answer(
        text="Введіть ціну тренувальної сесії:")
    await logger.add_message(event)


@coach_yes_admin_router.message(Price.price_session)
async def price(message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
                logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    if not message.text.isdigit():
        event = await message.answer(text="Введіть коректні дані:")
        await logger.add_message(event)

    else:

        await state.update_data(price_session=message.text)
        client_telegram_id = await chat_data.get_chat_data(message, "client_telegram_id")
        print('👉👉', client_telegram_id)

        data = await state.get_data()
        client_id = await orm_get_user_id_by_telegram_id(session=session, telegram_id=client_telegram_id)
        trainer_id = await orm_get_user_id_by_telegram_id(session=session, telegram_id=message.from_user.id)
        client_data = await orm_get_client_data(session, client_telegram_id)
        if client_data:
            print('👉👉', client_data)
            for date_client in client_data:
                (_, _, _, first_name, last_name, phone_nuber, price_per_session, start_date, end_data) = date_client
            if end_data is not None:
                await orm_update_client(
                    session=session,
                    trainer_id=trainer_id,
                    client_id=client_id,
                    price_per_session=data["price_session"])
                event = await bot.send_message(
                    client_telegram_id,
                    f"Заявка підтверджена",
                    reply_markup=await client_menu_button(session, client_telegram_id))
                await logger.add_message(event)

            else:
                await orm_update_price_per_session(
                    session=session,
                    client_id=client_id,
                    price_per_session=data["price_session"])
                event = await message.answer(
                    text="Ціна успішно змінена",
                    reply_markup=await training_client_details(
                        client_telegram_id, switch=True))
                await logger.add_message(event)

        else:
            await orm_add_trainer_clients(
                session=session,
                trainer_id=trainer_id,
                client_id=client_id,
                price_per_session=data["price_session"])
            event = await bot.send_message(
                client_telegram_id,
                f"Заявка підтверджена",
                reply_markup=await client_menu_button(session, client_telegram_id))
            await logger.add_message(event)
        await state.clear()
        await chat_data.clear_chat_data(message, ('client_telegram_id',))
