from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.chat_types import ChatTypeFilter
from middlewares.Safe_memory import ChatDataMiddleware

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))


@user_group_router.message(Command("admin"))
async def admin(message: Message, bot: Bot):
    user_list = await message.chat.get_administrators()
    admins_list = [user.user.id for user in user_list if user.custom_title == "admin"]
    creators_list = [user.user.id for user in user_list if user.custom_title == "creator"]
    bot.my_admins_list = admins_list
    print(bot.my_admins_list, "Admin - list")
    bot.my_creators_list = creators_list
    print(bot.my_creators_list, "Creator - list")

    if message.from_user.id in admins_list or creators_list:
        await message.delete()
