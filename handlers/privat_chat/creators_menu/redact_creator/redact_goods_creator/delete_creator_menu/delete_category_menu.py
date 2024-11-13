from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import get_category_buttons, verification_client
from database.func.table_products import orm_status_product_column

delete_category_router = Router()


@delete_category_router.callback_query(F.data.startswith("deletion_request_"))
async def handler_deletion_request(callback_query: CallbackQuery, state: FSMContext):
    category = callback_query.data.split("_")[-1]
    await callback_query.message.edit_text(
        text="УВАГА!\nПісля видалення категорії, товари із категорії також видаляються",
        reply_markup=await verification_client(
            startswith_yes="delete_category_",
            startswith_not=f"category_",
            telegram_id=category,
        ),
    )


@delete_category_router.callback_query(F.data.startswith("delete_category_"))
async def handler_delete_category(
        callback_query: CallbackQuery, state: FSMContext, session: AsyncSession
):
    category = callback_query.data.split("_")[-1]
    await orm_status_product_column(
        session=session,
        column="category",
        status_product="inactive",
        column_value=category,
    )
    await callback_query.message.edit_text(
        "Оберіть категорію:",
        reply_markup=await get_category_buttons(session, callback_query.from_user.id),
    )
