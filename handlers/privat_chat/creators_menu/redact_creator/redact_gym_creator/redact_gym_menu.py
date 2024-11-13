from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from buttons.creator_menu_button import creator_redact_gym_button
from middlewares.DelMessages import MessageLoggingMiddleware

redact_gym_router = Router()


@redact_gym_router.callback_query(F.data == "redact_gym")
async def handler_redact_gym(callback_query: CallbackQuery, state: FSMContext,
                             logger: MessageLoggingMiddleware, bot: Bot):
    await logger.del_all_messages(bot, callback_query)
    await state.clear()
    event = await callback_query.message.answer(
        f"Налаштовуйте ціну одноразових тренувань та абониментів: ",
        reply_markup=await creator_redact_gym_button())
    await logger.add_message(event)