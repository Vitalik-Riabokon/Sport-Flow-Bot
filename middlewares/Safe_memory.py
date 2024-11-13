from collections import defaultdict
from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class ChatDataMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.chat_data: defaultdict[int, dict[str, Any]] = defaultdict(dict)

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        data['chat_data'] = self
        return await handler(event, data)

    async def set_chat_data(self, event: CallbackQuery | Message | int, key: str, value: Any) -> None:
        if isinstance(event, Message):
            self.chat_data[event.from_user.id][key] = value
        elif isinstance(event, CallbackQuery):
            self.chat_data[event.from_user.id][key] = value
        elif isinstance(event, int):
            self.chat_data[event][key] = value

    async def get_chat_data(self, event: CallbackQuery | Message | int, key: str) -> Any:
        if isinstance(event, Message):
            return self.chat_data[event.from_user.id].get(key)
        elif isinstance(event, CallbackQuery):
            return self.chat_data[event.from_user.id].get(key)
        elif isinstance(event, int):
            return self.chat_data[event].get(key)

    async def print_all_chat_data(self) -> None:
        print("❗Всі дані чатів:", dict(self.chat_data))

    async def clear_chat_data(self, event: CallbackQuery | Message | int, keys: tuple[str, ...]) -> None:
        if isinstance(event, Message):
            telegram_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            telegram_id = event.from_user.id
        elif isinstance(event, int):
            telegram_id = event

        if telegram_id in self.chat_data:
            for key in keys:
                if key in self.chat_data[telegram_id]:
                    del self.chat_data[telegram_id][key]



