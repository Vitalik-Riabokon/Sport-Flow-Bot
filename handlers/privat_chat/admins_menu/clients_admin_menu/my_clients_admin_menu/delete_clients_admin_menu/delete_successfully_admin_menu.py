from aiogram import Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_trainer_clients import orm_update_end_data_client
from database.func.table_users import orm_get_user_id_by_telegram_id
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.my_client_admin_menu import \
    handler_check_client

delete_successfully_admin_router = Router()


@delete_successfully_admin_router.callback_query(lambda c: c.data.startswith("delete_successfully_"))
async def delete_successfully_(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession
):
    client_telegram_id = int(callback_query.data.split("_")[-1])
    client_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id
    )
    await orm_update_end_data_client(session, client_id)
    await handler_check_client(callback_query=callback_query, bot=bot, session=session)
    await callback_query.answer("Видалення клієнта успішне")
