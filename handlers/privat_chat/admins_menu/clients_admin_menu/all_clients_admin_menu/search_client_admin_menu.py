from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import get_all_client_buttons
from database.func.table_users import orm_get_user_by_name, orm_get_client_telegram_id, orm_get_name
from handlers.privat_chat.admins_menu.admin_menu import ClientName
from middlewares.DelMessages import MessageLoggingMiddleware

search_client_admin_router = Router()


@search_client_admin_router.callback_query(F.data == "search_client")
async def search_client(callback_query: CallbackQuery, state: FSMContext, bot: Bot, logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    await state.set_state(ClientName.client_name)
    event = await callback_query.message.answer(
        text="Введіть ім'я або прізвище, або повні ініціали користувача: ")
    await logger.add_message(event)


@search_client_admin_router.message(ClientName.client_name)
async def search_client_name(
        message: Message, state: FSMContext, bot: Bot, session: AsyncSession, logger: MessageLoggingMiddleware):
    user_list = []

    await logger.del_all_messages(bot, message)

    if len(message.text.split(" ")) == 2:
        input_first_name, input_last_name = message.text.split(" ")
        user = await orm_get_user_by_name(
            session=session, first_name=input_first_name, last_name=input_last_name
        )
        if user is not None:
            user_list.append((user.telegram_id, input_first_name, input_last_name))
        else:
            for telegram_id in await orm_get_client_telegram_id(session):
                output_first_name, output_got_last_name = await orm_get_name(
                    session, telegram_id
                )
                if (
                        input_first_name.lower() in output_first_name.lower()
                        and input_last_name.lower() in output_got_last_name.lower()
                ):
                    user_list.append(
                        (telegram_id, output_first_name, output_got_last_name)
                    )
    else:
        for telegram_id in await orm_get_client_telegram_id(session):
            first_name, last_name = await orm_get_name(session, telegram_id)
            if (
                    message.text.lower() in first_name.lower()
                    or message.text.lower() in last_name.lower()
            ):
                user_list.append((telegram_id, first_name, last_name))
    event = await message.answer(
        text="Оберіть користувача:",
        reply_markup=await get_all_client_buttons(session=session, user_list=user_list))
    await logger.add_message(event)
    await state.clear()
