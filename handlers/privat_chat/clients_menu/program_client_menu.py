from datetime import datetime

from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import admin_program_internal_detailing_button
from buttons.client_menu_button import client_program_month_button
from database.func.table_program_details import orm_check_program_details
from database.func.table_programs import orm_get_program, orm_check_program
from database.func.table_trainers import orm_get_trainer_id_by_user_id
from database.func.table_users import orm_get_user_id_by_telegram_id, orm_get_user_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

program_client_router = Router()


@program_client_router.callback_query(lambda c: c.data.startswith("program_choose_"))
async def handler_program_choose(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    client_month = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'client_month', client_month)
    client_telegram_id = await chat_data.get_chat_data(callback_query, 'client_telegram_id')
    trainer_telegram_id = await chat_data.get_chat_data(callback_query, 'trainer_telegram_id')
    user = await orm_get_user_by_telegram_id(session, callback_query.from_user.id)
    if user.status == 'client':
        switch = True
    else:
        switch = False
    event = await callback_query.message.answer(
        f"Дні тренувань:",
        reply_markup=await client_program_month_button(
            session,
            trainer_telegram_id,
            client_telegram_id,
            client_month,
            switch=switch))
    await logger.add_message(event)
    await callback_query.answer("Програма")


@program_client_router.callback_query(lambda c: c.data.startswith("view_program_"))
async def handler_view_program(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware):
    trainer_telegram_id = await chat_data.get_chat_data(callback_query, 'trainer_telegram_id')
    client_month = await chat_data.get_chat_data(callback_query, 'client_month')
    client_telegram_id = await chat_data.get_chat_data(callback_query, 'client_telegram_id')
    await logger.del_all_messages(bot, callback_query)

    day = int(callback_query.data.split("_")[-1])
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=trainer_telegram_id)

    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
    client_id = await orm_get_user_id_by_telegram_id(session=session, telegram_id=client_telegram_id)
    program_date = datetime(datetime.now().year, client_month, day).date()
    program_file = await orm_get_program(
        session=session,
        client_id=client_id,
        trainer_id=trainer_id,
        program_date=program_date)
    if program_file:
        try:
            event = await callback_query.message.answer_photo(
                program_file, caption="Ваша програма")
            await logger.add_message(event)
            event = await callback_query.message.answer(
                text="Дні тренувань:",
                reply_markup=await client_program_month_button(
                    session,
                    trainer_telegram_id,
                    client_telegram_id,
                    client_month))
            await logger.add_message(event)
        except Exception:
            try:
                event = await callback_query.message.answer_document(program_file, caption="Ваша програма")
                await logger.add_message(event)
                program = await orm_check_program(session, trainer_id, client_id, program_date)

                program_id = program.program_id
                await chat_data.set_chat_data(callback_query, 'program_id', program_id)

                if await orm_check_program_details(session, program_id):

                    event = await callback_query.message.answer(
                        text="Програма містити функціонал деталізації:",
                        reply_markup=await admin_program_internal_detailing_button(
                            program_id=program_id,
                            session=session,
                            client_telegram_id=client_telegram_id,
                            month=client_month))
                else:
                    event = await callback_query.message.answer(
                        text="Дні тренувань:",
                        reply_markup=await client_program_month_button(
                            session,
                            trainer_telegram_id,
                            client_telegram_id,
                            client_month))
                await logger.add_message(event)

            except Exception as e:
                event = await callback_query.message.answer(
                    f"Не вдалося відправити файл: {str(e)}")
                await logger.add_message(event)
    else:
        await callback_query.message.answer("Програма не знайдена на вказану дату.")
