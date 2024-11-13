from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.creator_menu_button import creator_redact_gym_button
from database.func.table_products import orm_get_product_name_by_category, orm_update_product
from handlers.privat_chat.creators_menu.creator_menu import Redact
from middlewares.DelMessages import MessageLoggingMiddleware

redact_one_time_training_router = Router()


@redact_one_time_training_router.callback_query(F.data == "redact_gym_one_time_training")
async def handler_redact_gym_one_time_training(
        callback_query: CallbackQuery, state: FSMContext, bot: Bot,
        logger: MessageLoggingMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    event = await callback_query.message.answer(
        f"Введіть нову ціну одноразового тренування",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(
                text="Назад🔙",
                callback_data=f"redact_gym")]]))
    await logger.add_message(event)
    await state.set_state(Redact.one_time_training)


@redact_one_time_training_router.message(Redact.one_time_training)
async def handler_one_time_training_price(message: Message, state: FSMContext, bot: Bot, session: AsyncSession,
                                          logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, message)

    if not message.text.isdigit():
        event = await message.answer(
            "Введіть коректні дані!", reply_markup=await creator_redact_gym_button()
        )
        await state.clear()
    else:

        category = "one_time_training"

        product_name = await orm_get_product_name_by_category(session, category=category)
        await orm_update_product(
            session, product_name[0], update_type=float(message.text), update_name="price"
        )
        await state.clear()
        event = await message.answer("Зміна ціни пройшла успішно!", reply_markup=await creator_redact_gym_button())
    await logger.add_message(event)
