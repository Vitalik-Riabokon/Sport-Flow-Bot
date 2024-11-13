from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.reg_log_but import start_button
from database.func.table_users import (orm_get_telegram_id,
                                       orm_get_user_by_name)
from middlewares.DelMessages import MessageLoggingMiddleware

login_router = Router()


class Login(StatesGroup):
    first_name = State()
    last_name = State()
    config = State()


@login_router.callback_query(lambda c: c.data == "start_login")
async def handler_start_login(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    user_telegram_id = callback_query.from_user.id
    if user_telegram_id in await orm_get_telegram_id(session=session):
        event = await callback_query.message.answer(
            "Ви вже зареєстровані.\nЩоб перейти на головне меню натисніть на /menu")
        await logger.add_message(event)
    else:

        await state.set_state(Login.first_name)
        event = await callback_query.message.answer("Введіть ваше ім'я:")
        await logger.add_message(event)


@login_router.message(Login.first_name)
async def handler_enter_first_name(message: types.Message, state: FSMContext, logger: MessageLoggingMiddleware,
                                   bot: Bot):
    await logger.del_all_messages(bot, message)
    await state.update_data(first_name=message.text)
    await state.set_state(Login.last_name)
    event = await message.answer("Введіть ваше прізвище:")
    await logger.add_message(event)


@login_router.message(Login.last_name)
async def handler_enter_last_name(
        message: types.Message, state: FSMContext, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, message)
    user_telegram_id = message.from_user.id
    if user_telegram_id in await orm_get_telegram_id(session=session):
        await message.answer("Ви вже зареєстровані.\nЩоб перейти на головне меню натисніть на /menu")
    else:
        await state.update_data(last_name=message.text)
        data = await state.get_data()
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        user = await orm_get_user_by_name(session=session, first_name=first_name, last_name=last_name)

        if user:
            event = await message.answer("Повідомлення з підтвердженням входу відправлено на основний акаунт.")
            await logger.add_message(event)

            await state.set_state(Login.config)
            event = await bot.send_message(
                user.telegram_id,
                text=f"Хтось намагається увійти у ваш акаунт з ім'ям {message.from_user.full_name}.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Підтвердити вхід",
                                callback_data=f"confirm_login_{message.from_user.id}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="Відхилити",
                                callback_data=f"deny_login_{message.from_user.id}")]]))
            await logger.add_message(event)

        else:
            await state.clear()
            event = await message.answer(
                "Користувача не знайдено. Спробуйте ще раз або зареєструйтесь.",
                reply_markup=start_button)
            await logger.add_message(event)
