from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import get_category_buttons
from database.func.table_products import orm_status_product_column

delete_product_router = Router()


@delete_product_router.callback_query(lambda c: c.data.startswith("delete_product_"))
async def handler_back_to_category(
        callback_query: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        session: AsyncSession,
):
    await state.clear()
    product_name = callback_query.data.split("_")[-1]
    await orm_status_product_column(
        session=session,
        column="product_name",
        status_product="inactive",
        column_value=product_name)
    await callback_query.message.edit_text(
        "Оберіть категорію:",
        reply_markup=await get_category_buttons(session, callback_query.from_user.id))
