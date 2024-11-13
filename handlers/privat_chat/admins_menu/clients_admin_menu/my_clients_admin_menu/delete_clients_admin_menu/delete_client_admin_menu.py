from aiogram import Router
from aiogram.types import CallbackQuery

from buttons.admin_buttons import del_client_button

delete_client_admin_router = Router()


@delete_client_admin_router.callback_query(lambda c: c.data.startswith("delete_client_"))
async def delete_client(callback_query: CallbackQuery):
    client_telegram_id = int(callback_query.data.split("_")[-1])
    await callback_query.message.edit_text(
        text="Ви впевнені що бажаєте видалити клієнта:",
        reply_markup=await del_client_button(client_telegram_id),
    )
    await callback_query.answer("Переконайтесь у вірності вашого рішення")
