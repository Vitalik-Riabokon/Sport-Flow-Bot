from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import admin_program_menu_button, admin_program_details_menu_button
from database.func.table_program_details import orm_check_program_details
from database.func.table_programs import orm_get_program, orm_check_program
from database.func.table_trainers import orm_get_trainer_id_by_user_id
from database.func.table_users import orm_get_user_id_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

check_program_admin_router = Router()


@check_program_admin_router.callback_query(F.data == "check_program")
async def handler_check_program(
        callback_query: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware
):
    client_telegram_id = await chat_data.get_chat_data(callback_query, 'client_telegram_id')
    month = await chat_data.get_chat_data(callback_query, 'month')
    day = await chat_data.get_chat_data(callback_query, 'day')
    await logger.del_all_messages(bot,callback_query)
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=callback_query.from_user.id)
    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
    client_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id)
    program_date = datetime(datetime.now().year, month, day).date()

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
                text="Оберіть дію:",
                reply_markup=await admin_program_menu_button(month, switch=False),
            )
            await logger.add_message(event)

        except Exception:
            try:
                event = await callback_query.message.answer_document(program_file, caption="Ваша програма")
                await logger.add_message(event)
                program = await orm_check_program(
                    session, trainer_id, client_id, program_date)

                program_id = program.program_id
                await chat_data.set_chat_data(callback_query, 'program_id', program_id)
                if await orm_check_program_details(session, program_id):
                    await callback_query.message.answer(
                        text="Програма містити функціонал деталізації вмісту файлу:",
                        reply_markup=await admin_program_details_menu_button(
                            day=day))
                else:
                    event = await callback_query.message.answer(
                        text="Оберіть дію:",
                        reply_markup=await admin_program_menu_button(
                            month, switch=False))
                    await logger.add_message(event)

            except Exception as e:
                await callback_query.message.answer(
                    f"Не вдалося відправити файл: {str(e)}"
                )
    else:
        event = await callback_query.message.answer("Програма не знайдена на вказану дату.")
        await logger.add_message(event)
