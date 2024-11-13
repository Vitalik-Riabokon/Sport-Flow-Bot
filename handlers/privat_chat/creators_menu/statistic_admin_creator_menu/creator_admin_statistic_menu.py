from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.creator_menu_button import creator_statistic_menu_button
from database.func.table_trainers import orm_get_trainer_id_by_user_id
from database.func.table_users import orm_get_user_id_by_telegram_id

statistic_router = Router()


@statistic_router.callback_query(F.data == "creator_statistic")
async def handler_creator_statistic(callback_query: CallbackQuery, session: AsyncSession):
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=callback_query.from_user.id)
    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)

    await callback_query.message.edit_text(
        text="Для більшої деталізації оберіть тип доходу: ",
        reply_markup=await creator_statistic_menu_button(session, trainer_id))
