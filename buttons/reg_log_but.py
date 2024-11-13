from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup)

start_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Реєстрація", callback_data="reg"),
            InlineKeyboardButton(text="Вхід", callback_data="start_login"),
        ]
    ]
)

button_data = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Ввести Ім'я", callback_data="first_name")],
        [InlineKeyboardButton(text="Ввести Прізвище", callback_data="last_name")],
        [InlineKeyboardButton(text="Ввести Номер", callback_data="number")],
        [InlineKeyboardButton(text="Закінчити реєстрацію", callback_data="check_data")]])


async def main_manu(status):
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Головне меню📰", callback_data=f"menu_{status}"
                )
            ]
        ]
    )
    return button


async def verification_reg_log(telegram_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Підтвердити", callback_data=f"finish_{telegram_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Відхилити", callback_data=f"discard_{telegram_id}"
                )
            ],
        ]
    )
