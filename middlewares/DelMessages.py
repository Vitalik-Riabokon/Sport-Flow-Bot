from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from collections import defaultdict


class MessageLoggingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.messages: defaultdict[int, list[int]] = defaultdict(list)
        self.callback_messages: defaultdict[int, list[int]] = defaultdict(list)

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            message_list = int(event.message_id)
            if event.text != '/start' and message_list not in self.messages[event.chat.id]:
                self.messages[event.chat.id].append(message_list)
                print(f"Message logged: {event.text}")
        elif isinstance(event, CallbackQuery):
            callback_list = int(event.message.message_id)
            if event.data != '/start' and callback_list not in self.callback_messages[event.message.chat.id]:
                self.callback_messages[event.message.chat.id].append(callback_list)
                print(f"Callback message logged: {event.data}")

        data['logger'] = self
        return await handler(event, data)

    async def print_all_messages(self) -> None:
        print("All messages:", self.messages)
        print("All callbacks:", self.callback_messages)

    async def del_all_messages(self, bot: Bot, event: Message | CallbackQuery) -> None:
        await self.print_all_messages()
        chat_id = event.chat.id if isinstance(event, Message) else event.message.chat.id

        message_ids = self.messages.pop(chat_id, [])
        for message_id in message_ids:
            try:
                await bot.delete_message(chat_id, message_id)
                print(f"Message deleted: {message_id}")
            except TelegramBadRequest as e:
                print(f"❗❗❗Error deleting message {message_id}: {e}")

        callback_message_ids = self.callback_messages.pop(chat_id, [])
        for message_id in callback_message_ids:
            try:
                await bot.delete_message(chat_id, message_id)
                print(f"Callback message deleted: {message_id}")
            except TelegramBadRequest as e:
                print(f"❗❗❗Error deleting callback message {message_id}: {e}")

    async def add_message(self, event: Message | CallbackQuery) -> None:
        if isinstance(event, Message):
            self.messages[event.chat.id].append(int(event.message_id))
        elif isinstance(event, CallbackQuery):
            self.callback_messages[event.message.message.chat.id].append(int(event.message.message_id))
