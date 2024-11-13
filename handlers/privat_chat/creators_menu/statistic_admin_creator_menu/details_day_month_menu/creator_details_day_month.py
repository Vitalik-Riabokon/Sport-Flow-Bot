from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.admin_buttons import month_button
from middlewares.Safe_memory import ChatDataMiddleware

detail_day_month_router = Router()


@detail_day_month_router.callback_query(F.data == "details_day_month")
async def handler_details_day_month(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                                    chat_data: ChatDataMiddleware):
    type_statistic = await chat_data.get_chat_data(callback_query, 'type_statistic')
    await callback_query.message.edit_text(
        text="Оберіть місяць: ",
        reply_markup=await month_button(session=session, type_statistic=type_statistic,
                                        telegram_id=callback_query.from_user.id, start_with="creator_",
                                        switch=True),
    )
    await callback_query.answer("Розділ деталей")
