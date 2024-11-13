from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, Message)
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.reg_log_but import (button_data, start_button,
                                 verification_reg_log)
from database.func.table_shifts import orm_get_active_shift
from database.func.table_users import (orm_get_telegram_id, orm_get_user_by_telegram_id, orm_get_trainer_full_name)
from filters.chat_types import ChatTypeFilter
from handlers.Error.custom_error import DataError, RegistrationError
from handlers.privat_chat.registration_menu.audit_reg_menu import handler_finish_registration
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

reg_router = Router()
reg_router.message.filter(ChatTypeFilter(["private"]))


class Reg(StatesGroup):
    first_name = State()
    last_name = State()
    number = State()


async def show_registration_menu(message: Message, state: FSMContext,
                                 logger: MessageLoggingMiddleware, bot: Bot, data_str: str = ''):
    data = await state.get_data()
    await logger.del_all_messages(bot, message)
    event = await message.answer(
        data_str + f"\nБудь ласка пройдіть реєстрацію"
                   f"\nІм'я: {data.get('first_name', '')}"
                   f"\nПрізвище: {data.get('last_name', '')}"
                   f"\nНомер телефону: {data.get('number', '')}",
        reply_markup=button_data)
    await logger.add_message(event)


@reg_router.callback_query(F.data == "reg")
async def handler_start_registration(callback_query: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession,
                                     logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    user_telegram_id = callback_query.from_user.id

    if user_telegram_id in await orm_get_telegram_id(session=session):
        event = await callback_query.message.answer(
            "Ви вже зареєстровані.\nЩоб перейти на головне меню натисніть на /menu")
        await logger.add_message(event)
    else:
        await show_registration_menu(callback_query.message, state, logger, bot)

        await callback_query.answer(text="Sport Flow")


@reg_router.message(Reg.first_name)
async def handler_enter_first_name(message: Message, state: FSMContext,
                                   logger: MessageLoggingMiddleware, bot: Bot):
    await logger.del_all_messages(bot, message)
    if not message.text.isalpha():
        event = await message.answer("Введіть коректні дані")
        await logger.add_message(event)

    else:
        await state.update_data(first_name=message.text)
        await show_registration_menu(message, state, logger, bot)


@reg_router.message(Reg.last_name)
async def handler_enter_last_name(message: Message, state: FSMContext, bot: Bot, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, message)
    if not message.text.isalpha():
        event = await message.answer("Введіть коректні дані")
        await logger.add_message(event)
    else:
        await state.update_data(last_name=message.text)
        await show_registration_menu(message, state, logger, bot)


@reg_router.message(Reg.number, F.contains)
async def handler_enter_number(message: Message, state: FSMContext, bot: Bot, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, message)

    if not message.text.isdigit():
        event = await message.answer("Введіть коректні дані")
        await logger.add_message(event)
    else:
        await state.update_data(number=message.text)
        await show_registration_menu(message, state, logger, bot)


@reg_router.callback_query(lambda query: query.data in ["first_name", "last_name", "number"])
async def handler_reg(callback_query: CallbackQuery, state: FSMContext):
    dict_state = {
        "first_name": Reg.first_name,
        "last_name": Reg.last_name,
        "number": Reg.number,
    }
    await state.set_state(dict_state[callback_query.data])

    state_text_map = {
        "first_name": "Введіть ваше ім'я:",
        "last_name": "Введіть ваше прізвище:",
        "number": "Введіть ваш номер телефону:",
    }

    await callback_query.message.edit_text(text=state_text_map[callback_query.data])
    await callback_query.answer()


@reg_router.callback_query(F.data == "check_data")
async def handler_check_data(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware, chat_data: ChatDataMiddleware):
    data = await state.get_data()
    for key, value in data.items():
        await chat_data.set_chat_data(callback_query, key, value)
    await chat_data.print_all_chat_data()
    await state.clear()
    try:
        if len(data) != 3:
            raise DataError("Не достатньо даних для завершенян реєстрації!")

        elif callback_query.from_user.id in await orm_get_telegram_id(session):
            await logger.del_all_messages(bot, callback_query)

            await callback_query.answer(
                "Ви вже зареєстровані будь ласка ввійдіть в акаунт!", show_alert=True
            )
            await callback_query.message.delete()

            raise RegistrationError("Ви вже зареєстровані")

        telegram_id = int(callback_query.from_user.id)
        active_shift = await orm_get_active_shift(session=session)
        if telegram_id in bot.my_admins_list or telegram_id in bot.my_creators_list:
            await logger.del_all_messages(bot, callback_query)
            await handler_finish_registration(callback_query, state, bot, session, logger, chat_data)
        elif active_shift is not None:
            user = await orm_get_trainer_full_name(session, active_shift.user_id)
            await callback_query.answer(
                "Очікуйте підтвердження працівником на рецепшені", show_alert=True)
            await callback_query.message.delete()
            event = await bot.send_message(
                user.telegram_id,
                text=f"Новий користувач. Перевірте коректність даних:"
                     f"\nІм'я: {await chat_data.get_chat_data(telegram_id, 'first_name')}"
                     f"\nПрізвище: {await chat_data.get_chat_data(telegram_id, 'last_name')}"
                     f"\nНомер телефону: {await chat_data.get_chat_data(telegram_id, 'number')}",
                reply_markup=await verification_reg_log(telegram_id=telegram_id))
            await logger.add_message(event)
        else:
            await logger.del_all_messages(bot, callback_query)
            await show_registration_menu(callback_query.message, state, logger, bot,
                                         data_str="На даний момент обслуговування не можливе! Зверніться до рецепшена\n")

    except RegistrationError:
        await logger.del_all_messages(bot, callback_query)

        event = await bot.send_message(
            callback_query.from_user.id,
            "Вас вітає команда Sport Flow🖐️", reply_markup=start_button)
        await logger.add_message(event)

    except DataError:
        await logger.del_all_messages(bot, callback_query)

        await show_registration_menu(callback_query.message, state, logger, bot,
                                     data_str="Введіть всі дані для завершення реєстрації!\n")
