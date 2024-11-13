from aiogram import Bot, F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery)
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.creator_menu_button import (creator_menu_button)
from filters.chat_types import ChatTypeFilter
from middlewares.DelMessages import MessageLoggingMiddleware

creator_router = Router()
creator_router.message.filter(ChatTypeFilter(["private"]))


class Redact(StatesGroup):
    one_time_training = State()
    membership_standard = State()
    membership_limitless = State()
    goods_name = State()
    goods_price = State()
    goods_photo = State()
    goods_description = State()
    category_name = State()
    new_category_name = State()
    old_category_name = State()


@creator_router.callback_query(F.data == "menu_creator")
async def creator_menu(callback_query: CallbackQuery, bot: Bot, session: AsyncSession,
                       logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    event = await callback_query.message.answer(
        "Оберіть дію:", reply_markup=await creator_menu_button(session, callback_query.from_user.id))
    await logger.add_message(event)
