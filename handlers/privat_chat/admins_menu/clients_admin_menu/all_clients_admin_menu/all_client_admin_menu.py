from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import get_all_client_buttons

all_client_admin_router = Router()


@all_client_admin_router.callback_query(F.data == "all_clients")
async def handler_all_clients(callback_query: CallbackQuery, bot: Bot, session: AsyncSession):
    await callback_query.message.edit_text(
        text="Для детальної інформації натисніть на особу:",
        reply_markup=await get_all_client_buttons(session))
