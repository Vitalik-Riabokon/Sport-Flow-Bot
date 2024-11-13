from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import validity_memberships_button

validity_memberships_admin_router = Router()


@validity_memberships_admin_router.callback_query(F.data == "validity_memberships")
async def validity_memberships(
        callback_query: CallbackQuery, bot: Bot, session: AsyncSession
):
    await callback_query.message.edit_text(
        "Для детальної інформації натисніть на особу:",
        reply_markup=await validity_memberships_button(session),
    )
