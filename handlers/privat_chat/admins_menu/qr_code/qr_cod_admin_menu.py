import os

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_trainers import orm_get_trainer_id_by_user_id, orm_get_trainer_details
from database.func.table_users import orm_get_user_id_by_telegram_id
from middlewares.DelMessages import MessageLoggingMiddleware
from dotenv import load_dotenv

load_dotenv()
qr_code_admin_router = Router()


@qr_code_admin_router.callback_query(F.data == "qr_code")
async def search_client(callback_query: CallbackQuery, session: AsyncSession, bot: Bot,
                        logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)

    file_name = os.getenv('QR_CODE_NAME')

    # Шукаємо файл в поточному каталозі та підкаталогах
    for root, dirs, files in os.walk('.'):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            break
    else:
        await callback_query.answer("Файл не знайдено. Зверніться до адміністратора.")
        return

    try:
        user_id = await orm_get_user_id_by_telegram_id(
            session=session, telegram_id=callback_query.from_user.id)
        trainer_id = await orm_get_trainer_id_by_user_id(session, user_id)
        data_user = await orm_get_trainer_details(session, trainer_id)

        if data_user[0]['status'] == "creator":
            callback_data = 'menu_creator'
        else:
            callback_data = 'menu_admin'

        # Використовуємо FSInputFile замість відкриття файлу
        photo = FSInputFile(file_path)
        event = await callback_query.message.answer_photo(
            photo=photo,
            caption="QR-code бота🤖", reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад🔙",
                            callback_data=callback_data,
                        )
                    ]
                ]))
        await logger.add_message(event)

    except Exception as e:
        print(f"Виникла помилка: {e}")
        await callback_query.answer("Виникла помилка при відправці файлу. Спробуйте пізніше.")
