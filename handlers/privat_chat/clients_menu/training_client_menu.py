from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import training_menu
from database.func.table_trainer_clients import orm_get_client_data
from database.func.table_trainers import orm_get_trainer_details

training_client_router = Router()

@training_client_router.callback_query(F.data == "training")
async def training(callback_query: CallbackQuery, bot: Bot, session: AsyncSession):
    client_telegram_id = callback_query.from_user.id
    for client_data in await orm_get_client_data(session, client_telegram_id):
        trainer_id = client_data[1]
    data_trainer = await orm_get_trainer_details(session, trainer_id)

    await callback_query.message.edit_text(
        f"Ваш тренер: {data_trainer[0]['first_name']} {data_trainer[0]['last_name']}\nОберіть операцію:",
        reply_markup=await training_menu(data_trainer[0]['telegram_id']),
    )
    await callback_query.answer("Розділ тренування")