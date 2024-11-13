from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from buttons.creator_menu_button import category_settings_buttons

category_settings_creator_router = Router()


@category_settings_creator_router.callback_query(F.data.startswith("settings_category_"))
async def handler_category_settings(callback_query: CallbackQuery, state: FSMContext):
    category = callback_query.data.split("_")[-1]
    await callback_query.message.edit_text(
        text="Оберіть зміну для категорії:",
        reply_markup=await category_settings_buttons(category),
    )
