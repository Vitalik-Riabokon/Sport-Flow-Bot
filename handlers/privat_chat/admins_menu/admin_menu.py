import os
from datetime import datetime

import pandas as pd
from aiogram import Bot, F, Router, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, Document, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import (admin_menu_button,
                                   admin_program_internal_detailing_button,
                                   admin_success_check_button,
                                   day_buttons, get_all_client_buttons)
from buttons.client_menu_button import verification_client
from database.func.table_program_details import (
    orm_add_program_details, orm_check_completed_days,
    orm_check_program_details, orm_get_program_details_data,
    orm_update_status_program_details, orm_del_program_details)
from database.func.table_programs import (orm_add_program, orm_check_program,
                                          orm_del_program)
from database.func.table_trainers import (orm_get_trainer_id_by_user_id)
from database.func.table_users import (orm_get_name, orm_get_user_id_by_telegram_id)
from filters.chat_types import ChatTypeFilter
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware
from mono_data.transaction_verification import get_last_incoming_transaction_today

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]))


class Program(StatesGroup):
    file_name = State()


class ClientName(StatesGroup):
    client_name = State()


@admin_router.callback_query(F.data == "menu_admin")
async def admin_menu(callback_query: CallbackQuery, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    first_name, last_name = await orm_get_name(
        session=session, telegram_id=callback_query.from_user.id)
    event = await callback_query.message.answer(
        f"{first_name} {last_name}🖐️\nЩо бажаєте?",
        reply_markup=await admin_menu_button(session, callback_query.from_user.id))
    await logger.add_message(event)


@admin_router.callback_query(F.data == "internal_detailing")
async def handler_internal_detailing(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware
):
    program_id = await chat_data.get_chat_data(callback_query, 'program_id')
    month = await chat_data.get_chat_data(callback_query, 'month')
    await logger.del_all_messages(bot, callback_query)
    await callback_query.message.answer(
        "Оберіть номер тренування:",
        reply_markup=await admin_program_internal_detailing_button(
            program_id=program_id,
            session=session,
            client_telegram_id=callback_query.from_user.id,
            month=month,
        ),
    )


@admin_router.callback_query(F.data == "check_completed_days")
async def handler_internal_detailing(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                                     chat_data: ChatDataMiddleware):
    program_id = await chat_data.get_chat_data(callback_query, 'program_id')
    text = "На даний момент даних не має"
    training_list = await orm_check_completed_days(session, program_id)

    if training_list:
        text = ""
        for program_data in training_list:
            training_number, program_status = program_data
            if program_status == "fail":
                program_status = "Невдача"
            else:
                program_status = "Успіх"

            text += f"Номер тренування№{training_number}\nРезультат тренування: {program_status}\n\n"
    await callback_query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Назад🔙", callback_data=f"internal_detailing"
                    )
                ]
            ]
        ),
    )


@admin_router.callback_query(lambda c: c.data.startswith("internal_detailing_program_"))
async def handler_internal_detailing_program(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, chat_data: ChatDataMiddleware
):
    training_number = int(callback_query.data.split("_")[-1])
    await chat_data.set_chat_data(callback_query, 'training_number', training_number)
    program_id = await chat_data.get_chat_data(callback_query, 'program_id')

    response = ""
    program_data = await orm_get_program_details_data(
        session=session, program_id=program_id, training_number=training_number)
    if program_data:
        response = f"Дані про тренування №{training_number}:\n"
        for row in program_data:
            approaches_number, repetitions_number, weight = row
            response += f"Кількість підходів: {approaches_number}, Повтори: {repetitions_number}, Вага: {weight}\n"

    await callback_query.message.edit_text(
        text=response, reply_markup=await admin_success_check_button()
    )


@admin_router.callback_query(lambda c: c.data.startswith("success_check_"))
async def handler_internal_detailing_program(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, chat_data: ChatDataMiddleware
):
    program_id = await chat_data.get_chat_data(callback_query, 'program_id')
    training_number = await chat_data.get_chat_data(callback_query, 'training_number')
    month = await chat_data.get_chat_data(callback_query, 'month')
    type_training = callback_query.data.split("_")[-1]
    await orm_update_status_program_details(
        session=session,
        program_status=type_training,
        program_id=program_id,
        training_number=training_number,
    )
    await callback_query.message.edit_text(
        "Оберіть номер тренування:",
        reply_markup=await admin_program_internal_detailing_button(
            program_id=program_id,
            session=session,
            client_telegram_id=callback_query.from_user.id,
            month=month,
        ),
    )


@admin_router.callback_query(F.data == "program_del")
async def handler_program_update(
        callback_query: types.CallbackQuery,
        bot: Bot,
        state: FSMContext,
        session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware
):
    client_telegram_id = await chat_data.get_chat_data(callback_query, 'client_telegram_id')
    month = await chat_data.get_chat_data(callback_query, 'month')
    day = await chat_data.get_chat_data(callback_query, 'day')
    await logger.del_all_messages(bot, callback_query)
    client_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id
    )
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=callback_query.from_user.id
    )
    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
    program_date = datetime(datetime.now().year, month, day).date()
    program = await orm_check_program(session=session, trainer_id=trainer_id,
                                      client_id=client_id, program_date=program_date)
    if await orm_check_program_details(session, program.program_id):
        await orm_del_program_details(session, program.program_id)
    await orm_del_program(
        session=session,
        trainer_id=trainer_id,
        client_id=client_id,
        program_date=program_date,
    )
    await callback_query.message.answer(text='Оберіть дію:',
                                        reply_markup=await day_buttons(session=session, month=month,
                                                                       client_telegram_id=client_telegram_id)
                                        )


@admin_router.message(Program.file_name)
async def program_file_name(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware
):
    client_telegram_id = await chat_data.get_chat_data(message, 'client_telegram_id')
    month = await chat_data.get_chat_data(message, 'month')
    day = await chat_data.get_chat_data(message, 'day')
    await logger.del_all_messages(bot, message)

    if (
            message.content_type == ContentType.TEXT
            or message.content_type == ContentType.VIDEO
    ):
        event = await message.answer(text="Надішліть файл або фото:")
        await logger.add_message(event)
    else:
        client_id = await orm_get_user_id_by_telegram_id(
            session=session, telegram_id=client_telegram_id
        )
        user_id = await orm_get_user_id_by_telegram_id(
            session=session, telegram_id=message.from_user.id
        )
        trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
        if message.content_type == ContentType.PHOTO:
            program_file = message.photo[-1].file_id
        elif message.content_type == ContentType.DOCUMENT:
            program_file = message.document.file_id

        program_date = datetime(datetime.now().year, month, day).date()

        await orm_add_program(
            session=session,
            trainer_id=trainer_id,
            client_id=client_id,
            program_file=program_file,
            program_date=program_date,
        )

        program = await orm_check_program(session, trainer_id, client_id, program_date)
        program_id = program.program_id

        if ".xlsx" in message.document.file_name:
            try:
                document: Document = message.document
                file_id = document.file_id

                # Отримання даних про файл з сервера Telegram
                file_info = await bot.get_file(file_id)
                file_path = file_info.file_path

                # Шлях до локального файлу
                local_file_path = f"downloads/{document.file_name}"

                # Переконатися, що директорія існує
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Завантаження файлу на локальний диск
                await bot.download_file(file_path, local_file_path)

                # Читання файлу
                read_excel_file = pd.read_excel(local_file_path, sheet_name="Тренування", header=1)
                print('🚫read_excel_file', read_excel_file)
                # Обробка даних
                await orm_add_program_details(session, program_id, read_excel_file)

            except Exception as e:
                print('EXCEPTION', e)

        event = await message.answer(
            text="Програма успішно добавлена: ",
            reply_markup=await day_buttons(session=session, month=month, client_telegram_id=client_telegram_id))
        await logger.add_message(event)
        await state.clear()


@admin_router.callback_query(lambda c: c.data.startswith("transaction_update_"))
async def handler_transaction_update(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                                     logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    await callback_query.message.delete()
    telegram_id = int(callback_query.data.split("_")[-1])
    first_name, last_name = await orm_get_name(session, telegram_id)
    product_name = await chat_data.get_chat_data(telegram_id, 'product_name')
    text = await get_last_incoming_transaction_today()

    event = await bot.send_message(
        callback_query.message.chat.id,
        text=f"{first_name} {last_name} бажає отримати: {product_name}. Вид оплати: карта\n\n" + text,
        reply_markup=await verification_client(
            startswith_yes="confirm_",
            startswith_not="negative_",
            telegram_id=telegram_id,
            startswith_middle='transaction_update_'),
    )
    await logger.add_message(event)


@admin_router.callback_query(lambda c: c.data.startswith("user_page_"))
async def user_page(callback_query: types.CallbackQuery, session: AsyncSession):
    _, category, page = callback_query.data.split("_")
    page = int(page)
    await callback_query.message.edit_text(
        f"Товари у категорії {category}:",
        reply_markup=await get_all_client_buttons(session=session, page=page),
    )
