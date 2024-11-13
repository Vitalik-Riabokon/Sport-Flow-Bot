from aiogram import Router, Bot, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import trainer_button, verification_client
from database.func.table_users import orm_get_name

trainer_client_router = Router()


class Price(StatesGroup):
    price_session = State()


@trainer_client_router.callback_query(F.data == "trainer")
async def trainer(callback_query: CallbackQuery, session: AsyncSession):
    await callback_query.message.edit_text(
        f"Оберіть тренера:", reply_markup=await trainer_button(session)
    )
    await callback_query.answer("Розділ тренерів")


@trainer_client_router.callback_query(lambda c: c.data.startswith("choose_"))
async def choose_coach(callback_query: CallbackQuery, bot: Bot, session: AsyncSession):
    trainer_telegram_id = int(callback_query.data.split("_")[-1])
    client_telegram_id = callback_query.from_user.id
    first_name, last_name = await orm_get_name(session, client_telegram_id)
    await callback_query.answer(
        "Дякую за вибір! Очікуйте на підтвердження обраного тренера", show_alert=True
    )
    await callback_query.message.delete()

    await bot.send_message(
        trainer_telegram_id,
        text=f"Клієнт {first_name} {last_name}, бажає бути вашим клієнтом",
        reply_markup=await verification_client(
            startswith_yes="coach_yes_",
            startswith_not="negative_",
            telegram_id=client_telegram_id,
        ),
    )
