from datetime import datetime

from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import client_menu_button
from buttons.reg_log_but import button_data
from database.func.table_trainers import orm_add_trainer
from database.func.table_users import orm_add_user
from handlers.privat_chat.admins_menu.admin_menu import admin_menu
from handlers.privat_chat.creators_menu.creator_menu import creator_menu
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

audit_reg_menu_router = Router()


@audit_reg_menu_router.callback_query(lambda c: c.data.startswith("finish_"))
async def handler_finish_registration(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    if callback_query.data.startswith("finish_"):
        telegram_id = int(callback_query.data.split("_")[-1])
    else:
        telegram_id = int(callback_query.from_user.id)

    if telegram_id in bot.my_admins_list:
        status_dict = {"status": "admin"}
        trainer_id = await orm_add_user(session=session, telegram_id=telegram_id,
                                        first_name=await chat_data.get_chat_data(telegram_id, 'first_name'),
                                        last_name=await chat_data.get_chat_data(telegram_id, 'last_name'),
                                        phone_number=await chat_data.get_chat_data(telegram_id, 'number'),
                                        status=status_dict["status"])
        event = await admin_menu(callback_query, bot, session, logger)
        await logger.add_message(event)
    elif telegram_id in bot.my_creators_list:
        status_dict = {"status": "creator"}
        trainer_id = await orm_add_user(session=session, telegram_id=telegram_id,
                                        first_name=await chat_data.get_chat_data(telegram_id, 'first_name'),
                                        last_name=await chat_data.get_chat_data(telegram_id, 'last_name'),
                                        phone_number=await chat_data.get_chat_data(telegram_id, 'number'),
                                        status=status_dict["status"])
        event = await creator_menu(callback_query, bot, session, logger)
        await logger.add_message(event)
    else:
        status_dict = {"status": "client"}
        trainer_id = await orm_add_user(session=session, telegram_id=telegram_id,
                                        first_name=await chat_data.get_chat_data(telegram_id, 'first_name'),
                                        last_name=await chat_data.get_chat_data(telegram_id, 'last_name'),
                                        phone_number=await chat_data.get_chat_data(telegram_id, 'number'),
                                        status=status_dict["status"])
        event = await bot.send_message(
            telegram_id,
            "Оберіть дію:",
            reply_markup=await client_menu_button(session, telegram_id))
        await logger.add_message(event)

    if status_dict["status"] != "client":
        await orm_add_trainer(session, trainer_id)

    await chat_data.clear_chat_data(telegram_id, ('first_name', 'last_name', 'number'))

    await chat_data.print_all_chat_data()


@audit_reg_menu_router.callback_query(lambda c: c.data.startswith("discard_"))
async def handler_refusal_registration(callback_query: CallbackQuery, bot: Bot, state: FSMContext,
                                       logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await callback_query.message.delete()
    telegram_id = int(callback_query.data.split("_")[-1])
    await chat_data.print_all_chat_data()
    event = await bot.send_message(
        telegram_id,
        text=f"Перевірте коректність даних:"
             f"\nІм'я: {await chat_data.get_chat_data(telegram_id, 'first_name')}"
             f"\nПрізвище: {await chat_data.get_chat_data(telegram_id, 'last_name')}"
             f"\nНомер телефону: {await chat_data.get_chat_data(telegram_id, 'number')}",
        reply_markup=button_data)
    await logger.add_message(event)
