from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.client_menu_button import get_product_buttons
from database.func.table_products import orm_get_product_name_by_category
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware

search_product_client_router = Router()


class SearchProducts(StatesGroup):
    search_product = State()


@search_product_client_router.callback_query(F.data == "search_product")
async def handler_search_product(
        callback_query: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession,
        logger: MessageLoggingMiddleware):
    await logger.del_all_messages(bot, callback_query)
    await state.set_state(SearchProducts.search_product)
    event = await callback_query.message.answer(
        text="Введіть повну або часткову назву товару: ")
    await logger.add_message(event)


@search_product_client_router.message(SearchProducts.search_product)
async def handler_result_product(
        message: Message, bot: Bot, state: FSMContext, session: AsyncSession, logger: MessageLoggingMiddleware,
        chat_data: ChatDataMiddleware):
    await logger.del_all_messages(bot, message)
    category = await chat_data.get_chat_data(message, 'category')
    product_list = []
    if len(message.text.split(" ")) > 1:
        input_first_name, input_last_name = (
            message.text.split(" ")[0],
            message.text.split(" ")[-1],
        )

        for product in await orm_get_product_name_by_category(session, category):
            if (
                    input_first_name.lower() in product.split(" ")[0].lower()
                    and input_last_name.lower() in product.split(" ")[-1].lower()
            ):
                product_list.append(product)
    elif len(message.text.split(" ")) == 1:
        for product in await orm_get_product_name_by_category(session, category):
            if message.text.lower() in product.lower():
                product_list.append(product)

    event = await message.answer(
        text="Оберіть користувача:",
        reply_markup=await get_product_buttons(session,
                                               category=category,
                                               products_list=product_list,
                                               telegram_id=message.from_user.id))
    await logger.add_message(event)
    await state.clear()
