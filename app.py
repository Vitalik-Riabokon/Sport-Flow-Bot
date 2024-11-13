import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import (BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats)

from database.engine import async_session, create_tables
from middlewares.DelMessages import MessageLoggingMiddleware
from middlewares.Safe_memory import ChatDataMiddleware
from middlewares.db_middleware import DataBaseSession
from my_router.my_routers import activate_router
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

bot.change_category = []
bot.my_admins_list = []
bot.my_creators_list = []
bot.category = []


async def set_commands(bot: Bot):
    # Команди для приватних чатів
    private_chat_commands = [
        BotCommand(command="/start", description="Меню реєстрації та входу🎫"),
        BotCommand(command="/menu", description="Ваше головне меню🪪"),
    ]
    # Команди для групових чатів
    group_chat_commands = [
        BotCommand(command="/admin", description="Адміністративна команда"),
    ]
    await bot.set_my_commands(
        private_chat_commands,
        scope=BotCommandScopeAllPrivateChats()
    )
    await bot.set_my_commands(group_chat_commands, scope=BotCommandScopeAllGroupChats())


async def on_startup():
    logging.info("Бот запущено")
    # await drop_db()
    await create_tables()


async def main():
    message_logger = MessageLoggingMiddleware()
    chat_data = ChatDataMiddleware()
    for data in [message_logger, chat_data]:
        dp.message.middleware(data)
        dp.callback_query.middleware(data)

    dp.startup.register(on_startup)
    dp.update.middleware(DataBaseSession(session_pool=async_session))
    await set_commands(bot)
    dp.include_routers(*await activate_router())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
