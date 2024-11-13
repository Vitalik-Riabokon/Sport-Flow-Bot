import calendar
from datetime import datetime

from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_payments import orm_get_validity_memberships, orm_get_months_with_data, orm_get_days_with_data
from database.func.table_program_details import \
    orm_get_program_details_training_number
from database.func.table_shifts import orm_get_active_shift
from database.func.table_trainer_clients import (
    orm_get_client_full_name_tg_id)
from database.func.table_trainers import orm_get_trainer_details
from database.func.table_users import (orm_get_client_telegram_id,
                                       orm_get_name, orm_get_user_by_telegram_id)


async def admin_program_menu_button(month, switch=True):
    keyboard = InlineKeyboardBuilder()

    if switch:
        keyboard.add(
            InlineKeyboardButton(text="Переглянути", callback_data=f"check_program")
        )

    keyboard.add(
        InlineKeyboardButton(text="Видалити", callback_data=f"program_del"),
        InlineKeyboardButton(text="Назад🔙", callback_data=f"month_{month}"),
    )

    keyboard.adjust(1, 1)

    return keyboard.as_markup()


async def admin_program_details_menu_button(day):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Деталі програми", callback_data=f"internal_detailing"
                )
            ],
            [InlineKeyboardButton(text="Назад🔙", callback_data=f"day_{day}")],
        ]
    )

    return keyboard


async def admin_program_internal_detailing_button(
        program_id, session: AsyncSession, client_telegram_id=None, month=None
):
    keyboard = InlineKeyboardBuilder()
    for training_number in await orm_get_program_details_training_number(
            session, program_id
    ):
        keyboard.add(
            InlineKeyboardButton(
                text=f"№{training_number}",
                callback_data=f"internal_detailing_program_{training_number}",
            )
        )
    keyboard.adjust(3, 3)
    keyboard.row(
        InlineKeyboardButton(
            text=f"Переглянути пройдені дні", callback_data=f"check_completed_days"
        )
    )
    if month is not None and client_telegram_id in await orm_get_client_telegram_id(
            session
    ):
        keyboard.row(
            InlineKeyboardButton(
                text=f"Назад🔙", callback_data=f"program_choose_{month}"
            )
        )

    else:
        keyboard.row(
            InlineKeyboardButton(text=f"Назад🔙", callback_data=f"check_program")
        )

    return keyboard.as_markup()


async def admin_success_check_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text=f"Успіх", callback_data=f"success_check_success"),
        InlineKeyboardButton(text=f"Невдача", callback_data=f"success_check_fail"),
    )
    keyboard.adjust(1, 1)
    keyboard.row(
        InlineKeyboardButton(text=f"Назад🔙", callback_data=f"internal_detailing")
    )
    return keyboard.as_markup()


# Функція для створення інлайн-клавіатури з місяцями
async def month_button(session, client_telegram_id=None, type_statistic=None, telegram_id=None, switch=False,
                       start_with=""):
    keyboard = InlineKeyboardBuilder()
    months_uk = [
        "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень",
        "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
    ]
    months_with_data = await orm_get_months_with_data(session, type_statistic, telegram_id)

    for i, month in enumerate(months_uk, start=1):
        if switch:
            if i in months_with_data:
                keyboard.add(
                    InlineKeyboardButton(text=month, callback_data=f"{start_with}month_{i}")
                )
        else:
            keyboard.add(
                InlineKeyboardButton(text=month, callback_data=f"{start_with}month_{i}")
            )
    keyboard.adjust(3, 3)

    if switch:
        keyboard.row(
            InlineKeyboardButton(text="Назад🔙", callback_data=f"creator_statistic")
        )
    else:
        keyboard.row(
            InlineKeyboardButton(
                text="Назад🔙", callback_data=f"client_data_{client_telegram_id}"
            )
        )

    return keyboard.as_markup()


# Функція для створення інлайн-клавіатури з днями місяця
async def day_buttons(session, month: int, type_statistic=None, telegram_id=None, client_telegram_id=None,
                      start_with="", switch=False):
    year: int = datetime.now().year
    keyboard = InlineKeyboardBuilder()
    days_in_month = calendar.monthrange(year, month)[1]

    days_with_data = await orm_get_days_with_data(session, type_statistic, month, telegram_id)

    for day in range(1, days_in_month + 1):
        if switch:
            if day in days_with_data:
                keyboard.add(
                    InlineKeyboardButton(text=str(day), callback_data=f"{start_with}day_{day}")
                )
        else:

            keyboard.add(
                InlineKeyboardButton(text=str(day), callback_data=f"{start_with}day_{day}")
            )
    keyboard.adjust(7, 7)
    if switch:
        keyboard.row(
            InlineKeyboardButton(text="Назад🔙", callback_data=f"details_day_month")
        )
    else:
        keyboard.row(
            InlineKeyboardButton(
                text="Назад🔙",
                callback_data=f"training_client_program_{client_telegram_id}",
            )
        )
    return keyboard.as_markup()


async def admin_menu_button(session, telegram_id):
    shift = await orm_get_active_shift(session)
    active_shift = None if shift is None else shift.user_id

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Зал", callback_data="clients"))
    user = await orm_get_user_by_telegram_id(session, telegram_id)

    if user.status == "creator":
        keyboard.add(InlineKeyboardButton(text="Товари", callback_data="goods_switch"))
        keyboard.add(InlineKeyboardButton(text="Налаштування", callback_data="redact"))
    elif user.status == "admin":
        keyboard.add(InlineKeyboardButton(text="Товари", callback_data="goods"))
    keyboard.add(InlineKeyboardButton(text="QR-code", callback_data="qr_code"))
    user = await orm_get_user_by_telegram_id(session, telegram_id)
    if user.user_id == active_shift:
        keyboard.add(
            InlineKeyboardButton(text="Закрити зміну", callback_data="close_work")
        )
    else:
        keyboard.add(
            InlineKeyboardButton(text="Відкрити зміну", callback_data="open_work")
        )

    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def client_pagination_buttons(current_page, total_pages):
    admin_buttons = []
    if current_page > 0:
        admin_buttons.append(
            InlineKeyboardButton(
                text="Назад⏪", callback_data=f"user_page_{current_page - 1}"
            )
        )
    if current_page < total_pages - 1:
        admin_buttons.append(
            InlineKeyboardButton(
                text="Далі⏩", callback_data=f"user_page_{current_page + 1}"
            )
        )
    return admin_buttons


async def get_all_client_buttons(session: AsyncSession, page=0, user_list=None):
    items_per_page = 9
    if user_list is None:
        user_list = [
            [telegram_id, *await orm_get_name(session, telegram_id)]
            for telegram_id in await orm_get_client_telegram_id(session=session)
        ]
        user_list.sort(key=lambda x: x[1])

    start_index = page * items_per_page
    end_index = start_index + items_per_page
    page_items = user_list[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    for user in page_items:
        telegram_id, first_name, last_name = user
        keyboard.add(
            InlineKeyboardButton(
                text=f"{first_name} {last_name}",
                callback_data=f"user_data_{telegram_id}",
            )
        )
    keyboard.adjust(3, 3)

    total_pages = (len(user_list) + items_per_page - 1) // items_per_page
    pagination_buttons = await client_pagination_buttons(page, total_pages)

    if pagination_buttons:
        keyboard.row(*pagination_buttons)

    keyboard.row(InlineKeyboardButton(text="Пошук🔎", callback_data="search_client"))
    keyboard.row(
        InlineKeyboardButton(
            text="Абонименти, які закінчуються⌛", callback_data="validity_memberships"
        )
    )
    keyboard.row(
        InlineKeyboardButton(text="Розділ клієнтів⏪", callback_data="clients")
    )
    return keyboard.as_markup()


async def client_data_button(session, trainer_id):
    keyboard = InlineKeyboardBuilder()
    for client in await orm_get_client_full_name_tg_id(session, trainer_id):
        telegram_id, first_name, last_name = client
        keyboard.add(
            InlineKeyboardButton(
                text=f"{first_name} {last_name}",
                callback_data=f"client_data_{telegram_id}",
            )
        )
    keyboard.adjust(3, 3)

    keyboard.row(InlineKeyboardButton(text="Денний дохід💰", callback_data="cash_day"))
    keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data="clients"))
    return keyboard.as_markup()


async def validity_memberships_button(session):
    keyboard = InlineKeyboardBuilder()
    for client in await orm_get_validity_memberships(session):
        telegram_id, first_name, last_name, _, _, _, _, _ = client
        keyboard.add(
            InlineKeyboardButton(
                text=f"{first_name} {last_name}",
                callback_data=f"user_memberships_{telegram_id}",
            )
        )
    keyboard.adjust(3, 3)

    keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data="all_clients"))
    return keyboard.as_markup()


async def training_client_details(client_telegram_id, switch=False):
    print(client_telegram_id)
    keyboard = InlineKeyboardBuilder()

    if switch:
        keyboard.add(
            InlineKeyboardButton(
                text="Абонимент🪪",
                callback_data=f"client_memberships_{client_telegram_id}",
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="Змінити ціну сеансу💸",
                callback_data=f"coach_yes_{client_telegram_id}",
            ),

            InlineKeyboardButton(
                text="Налаштування програм⚙️",
                callback_data=f"training_client_program_{client_telegram_id}",
            ),
            InlineKeyboardButton(
                text="Перегляд програм📄",
                callback_data=f"client_program_{client_telegram_id}",
            ),
            InlineKeyboardButton(
                text="Видалити клієнта🫠",
                callback_data=f"delete_client_{client_telegram_id}",
            ),
            InlineKeyboardButton(text="Назад🔙", callback_data="my_clients"),
        )
    else:
        keyboard.add(
            InlineKeyboardButton(
                text="Абонимент🪪",
                callback_data=f"user_memberships_{client_telegram_id}",
            )
        )
        keyboard.add(InlineKeyboardButton(text="Назад🔙", callback_data="all_clients"))

    keyboard.adjust(1, 1)

    return keyboard.as_markup()


async def del_client_button(client_telegram_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Так",
                    callback_data=f"delete_successfully_{client_telegram_id}",
                )
            ],
            [InlineKeyboardButton(
                text="Ні", callback_data=f"client_data_{client_telegram_id}"
            )
            ],
        ]
    )
    return keyboard


async def clients_button():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(text=f"Мої клієнти", callback_data=f"my_clients"),
        InlineKeyboardButton(text=f"Всі клієнти", callback_data=f"all_clients"),
    )
    keyboard.adjust(1, 1)

    keyboard.row(
        InlineKeyboardButton(text=f"Статистика", callback_data=f"creator_statistic")
    )
    keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data="menu_admin"))
    return keyboard.as_markup()
