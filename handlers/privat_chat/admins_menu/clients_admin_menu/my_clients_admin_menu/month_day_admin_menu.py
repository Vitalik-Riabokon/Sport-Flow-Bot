from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import day_buttons, admin_program_menu_button
from database.func.table_programs import orm_check_program
from database.func.table_trainers import orm_get_trainer_id_by_user_id
from database.func.table_users import orm_get_user_id_by_telegram_id
from handlers.privat_chat.admins_menu.admin_menu import Program
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

month_day_admin_router = Router()


@month_day_admin_router.callback_query(F.data.startswith("month_"))
async def month_callback(callback_query: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession,
                         logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, callback_query)
    await state.clear()
    month = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'month', month)
    client_telegram_id = await chat_data.get_chat_data(callback_query, 'client_telegram_id')
    event = await callback_query.message.answer(
        text="Оберіть дію: ",
        reply_markup=await day_buttons(session=session, month=month, client_telegram_id=client_telegram_id))
    await logger.add_message(event)


# Обробник callback-запитів для днів
@month_day_admin_router.callback_query(F.data.startswith("day_"))
async def day_callback(
        callback_query: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        session: AsyncSession,
        logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware,
):
    await logger.del_all_messages(bot, callback_query)

    day = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'day', day)
    month = await chat_data.get_chat_data(callback_query, 'month')
    client_telegram_id = await chat_data.get_chat_data(callback_query, 'client_telegram_id')

    date_obj = datetime(datetime.now().year, month, day).date()
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=callback_query.from_user.id
    )
    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
    client_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id
    )
    program = await orm_check_program(session, trainer_id, client_id, date_obj)
    if program:
        event = await callback_query.message.answer(
            text="Цей день вже містить програму: ",
            reply_markup=await admin_program_menu_button(month))
        await logger.add_message(event)

    else:
        await state.set_state(Program.file_name)
        event = await callback_query.message.answer(
            text="Надішліть файл або фото:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад🔙", callback_data=f"month_{month}"
                        )]]))
        await logger.add_message(event)
