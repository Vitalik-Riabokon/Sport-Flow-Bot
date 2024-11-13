from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import client_data_button, training_client_details
from database.func.table_users import orm_get_user_id_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

my_client_admin_router = Router()


@my_client_admin_router.callback_query(F.data == "my_clients")
async def handler_check_client(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession, chat_data: ChatDataMiddleware,
        logger: MessageLoggingMiddleware
):
    await logger.del_all_messages(bot, callback_query)
    my_chat_id = callback_query.message.chat.id
    await chat_data.set_chat_data(callback_query, 'my_chat_id', my_chat_id)

    trainer_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=callback_query.from_user.id)
    event = await callback_query.message.answer(
        f"Ваші клієнти:", reply_markup=await client_data_button(session, trainer_id))
    await logger.add_message(event)


@my_client_admin_router.callback_query(lambda c: c.data.startswith("client_data_"))
async def client_details(callback_query: CallbackQuery, bot: Bot, state: FSMContext,
                         logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    client_telegram_id = int(callback_query.data.split("_")[-1])
    await state.clear()
    await callback_query.message.answer(
        f"Оберіть операцію над клієнтом:",
        reply_markup=await training_client_details(client_telegram_id, switch=True))
