from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.creator_menu_button import creator_redact_gym_button, creator_type_membership_button
from database.func.table_products import orm_update_product
from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware

redact_membership_router = Router()


@redact_membership_router.callback_query(F.data == "redact_gym_membership")
async def handler_redact_gym_membership(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    event = await callback_query.message.answer(
        f"Оберіть вид абонименту:", reply_markup=await creator_type_membership_button())
    await logger.add_message(event)


@redact_membership_router.callback_query(F.data == "redact_gym_membership_standard")
async def handler_redact_gym_membership_standard(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    event = await callback_query.message.answer(
        f"Введіть нову ціну абонимента:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Назад🔙",
                        callback_data=f"redact_gym_membership",
                    )
                ]
            ]
        ),
    )
    await logger.add_message(event)
    await state.set_state(Redact.membership_standard)


@redact_membership_router.message(Redact.membership_standard)
async def handler_membership_standard(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, message)

    if not message.text.isdigit():
        event = await message.answer(
            "Введіть коректні дані!",
            reply_markup=await creator_redact_gym_button(),
        )
        await state.clear()

    else:
        await orm_update_product(
            session, "Стандарт", update_type=float(message.text), update_name="price"
        )
        await state.clear()
        event = await message.answer(
            "Зміна ціни пройшла успішно!",
            reply_markup=await creator_redact_gym_button(),
        )
    await logger.add_message(event)


@redact_membership_router.callback_query(F.data == "redact_gym_membership_limitless")
async def handler_redact_gym_membership_limitless(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    event = await callback_query.message.answer(
        f"Введіть нову ціну абонимента:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Назад🔙",
                        callback_data=f"redact_gym_membership",
                    )
                ]
            ]
        ),
    )
    await logger.add_message(event)
    await state.set_state(Redact.membership_limitless)


@redact_membership_router.message(Redact.membership_limitless)
async def handler_one_time_training_price(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
        logger: MessageLoggingMiddleware
):
    await logger.del_all_messages(bot, message)
    if not message.text.isdigit():
        event = await message.answer(
            text="Введіть коректні дані!", reply_markup=await creator_redact_gym_button()
        )
        await state.clear()

    else:
        await orm_update_product(
            session, "Безлім", update_type=float(message.text), update_name="price"
        )
        await state.clear()

        event = await message.answer(
            "Зміна ціни пройшла успішно!", reply_markup=await creator_redact_gym_button())
    await logger.add_message(event)