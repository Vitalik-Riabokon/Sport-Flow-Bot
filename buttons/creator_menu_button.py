from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from buttons.admin_buttons import admin_menu_button
from database.func.table_trainers import orm_get_trainer_details

creator_menu_button = admin_menu_button


async def creator_statistic_menu_button(session, trainer_id):
    keyboard = InlineKeyboardBuilder()
    data_user = await orm_get_trainer_details(session, trainer_id)
    keyboard.add(InlineKeyboardButton(text="Клієнти", callback_data="creator_statistic_menu_client"))

    if data_user[0]['status'] == "creator":
        keyboard.row(InlineKeyboardButton(text="Зал", callback_data="creator_statistic_menu_gym"))
        keyboard.row(InlineKeyboardButton(text="Товари", callback_data="creator_statistic_menu_goods"))

    keyboard.row(InlineKeyboardButton(text="Головне меню🔙", callback_data="clients"))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def creator_redact_menu_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Редагування залу", callback_data=f"redact_gym"),
        InlineKeyboardButton(text="Редагування Товарів", callback_data=f"goods"),
        InlineKeyboardButton(text="Головне меню🔙", callback_data=f"menu_creator"),
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def creator_redact_gym_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Зміна ціни абонименту", callback_data=f"redact_gym_membership"
        ),
        InlineKeyboardButton(
            text="Зміна ціни одноразового тренування",
            callback_data=f"redact_gym_one_time_training",
        ),
        InlineKeyboardButton(text="Налаштування🔙", callback_data=f"redact"),
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def creator_type_membership_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Абонимент стандарт", callback_data=f"redact_gym_membership_standard"
        ),
        InlineKeyboardButton(
            text="Абонимент безлім", callback_data=f"redact_gym_membership_limitless"
        ),
        InlineKeyboardButton(text="Назад🔙", callback_data=f"redact_gym"),
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def check_details_menu_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Місячні та денні деталі", callback_data=f"details_day_month"
        ),
        InlineKeyboardButton(text="Назад🔙", callback_data=f"creator_statistic"),
    )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def next_redact_button(
    category, product=None, category_switch=False, del_switch=False
):
    keyboard = InlineKeyboardBuilder()
    if not category_switch:
        if del_switch:
            keyboard.row(
                InlineKeyboardButton(
                    text="Видалити товар🚫", callback_data=f"delete_product_{product}"
                )
            )
        keyboard.row(
            InlineKeyboardButton(text="Пропустити⏭️", callback_data=f"next_redact")
        )
    if category and not category_switch:
        keyboard.row(
            InlineKeyboardButton(
                text="Назад до товарів⏪", callback_data=f"back_to_category_{category}"
            )
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="Назад до категорій⏪", callback_data=f"goods")
        )

    return keyboard.as_markup()


async def category_settings_buttons(category):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Добавити новий товар✨", callback_data=f"add_new_product_{category}"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Видалити категорію🚫", callback_data=f"deletion_request_{category}"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Змінити назву категорії🔁",
            callback_data=f"change_category_name_{category}",
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Назад до товарів⏪", callback_data=f"back_to_category_{category}"
        )
    )

    return keyboard.as_markup()
