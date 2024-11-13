from collections import defaultdict
from datetime import datetime

from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_products import (orm_get_all_category,
                                          orm_get_product_details,
                                          orm_get_product_name_by_category)
from database.func.table_programs import orm_check_all_training
from database.func.table_trainer_clients import orm_get_client_id
from database.func.table_trainers import (orm_get_trainer_id_by_user_id,
                                          orm_get_trainers)
from database.func.table_users import (orm_get_trainer_full_name,
                                       orm_get_user_by_telegram_id,
                                       orm_get_user_id_by_telegram_id)

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Головне меню")],
    ],
    resize_keyboard=True,
)

buy_membership_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Стандарт✨", callback_data="buy_Стандарт")],
        [InlineKeyboardButton(text="Безлім😎", callback_data="buy_Безлім")],
        [InlineKeyboardButton(text="Назад🔙", callback_data="menu_client")],
    ]
)


async def client_menu_button(session, telegram_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Абонимент", callback_data="memberships"),
        InlineKeyboardButton(
            text="Одноразове тренування", callback_data="one_time_training"
        ),
        InlineKeyboardButton(text="Товари", callback_data="goods"),
        InlineKeyboardButton(text="Графік роботи", callback_data="schedule"),
    )
    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=telegram_id
    )

    if user_id in await orm_get_client_id(session):
        keyboard.add(InlineKeyboardButton(text="Тренування", callback_data="training"))
    else:
        keyboard.add(
            InlineKeyboardButton(text="Обрати тренера", callback_data="trainer")
        )
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def training_menu(trainer_telegram_id):
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Програма📄",
                    callback_data=f"client_program_{trainer_telegram_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Оплата тренування💸",
                    callback_data=f"payment_training_{trainer_telegram_id}",
                )
            ],
            [InlineKeyboardButton(text="Назад🔙", callback_data="menu_client")],
        ]
    )
    return button


async def type_buy_button(callbackcash, callbackcard, callback):
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Готівка💰", callback_data=callbackcash)],
            [InlineKeyboardButton(text="Карта💳", callback_data=callbackcard)],
            [InlineKeyboardButton(text="Назад🔙", callback_data=callback)],
        ]
    )
    return button


async def verification_client(startswith_yes, startswith_not, telegram_id, startswith_middle=None):
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(text="Підтвердити👍", callback_data=f"{startswith_yes}{telegram_id}"
                                      ))
    if startswith_middle is not None:
        print(f'{startswith_middle}{telegram_id}')
        keyboard.row(InlineKeyboardButton(text="Оновити дані🤖", callback_data=f"{startswith_middle}{telegram_id}"
                                          ))
    keyboard.row(InlineKeyboardButton(text="Відхилити👎", callback_data=f"{startswith_not}{telegram_id}"
                                      ))
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


async def get_category_buttons(session, telegram_id, page=0, switch_creator=True):
    categories = await orm_get_all_category(session)
    print(categories)
    items_per_page = 6
    start_index = page * items_per_page
    end_index = start_index + items_per_page
    page_categories = categories[start_index:end_index]

    keyboard = InlineKeyboardBuilder()
    for category in page_categories:
        keyboard.add(
            InlineKeyboardButton(text=category, callback_data=f"category_{category}")
        )
    keyboard.adjust(2, 2)

    user = await orm_get_user_by_telegram_id(session, telegram_id)
    if user.status == "creator" and page == 0 and switch_creator:
        keyboard.row(
            InlineKeyboardButton(
                text="Добавити нову категорію✨", callback_data="add_new_category"
            )
        )
    else:
        keyboard.row(InlineKeyboardButton(text="Кошик🧺", callback_data="basket"))

    total_pages = (len(categories) + items_per_page - 1) // items_per_page
    pagination_buttons = await create_pagination_buttons(page, total_pages, "category")

    if pagination_buttons:
        keyboard.row(*pagination_buttons)

    if user.status == "creator":
        if switch_creator:
            keyboard.row(
                InlineKeyboardButton(text="Налаштування🔙", callback_data="redact")
            )
        else:
            keyboard.row(
                InlineKeyboardButton(text="Головне меню🔙", callback_data="menu_creator")
            )
    elif user.status == "admin":
        keyboard.row(
            InlineKeyboardButton(text="Головне меню🔙", callback_data="menu_admin")
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="Головне меню🔙", callback_data="menu_client")
        )

    return keyboard.as_markup()


async def create_pagination_buttons(current_page, total_pages, category):
    buttons = []
    if current_page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="Назад⏪", callback_data=f"page_{category}_{current_page - 1}"
            )
        )
    if current_page < total_pages - 1:
        buttons.append(
            InlineKeyboardButton(
                text="Далі⏩", callback_data=f"page_{category}_{current_page + 1}"
            )
        )
    return buttons


async def get_product_buttons(session, category, page=0, products_list=None, telegram_id=None, switch_creator=True):
    switch = True
    if products_list is not None:
        switch = False

    if page == 0:
        items_per_page = 4
        start_index = page * items_per_page

    else:
        items_per_page = 6
        start_index = page * items_per_page - 2

    if products_list is None:
        products_list = await orm_get_product_name_by_category(session, category)
    end_index = start_index + items_per_page
    page_items = products_list[start_index:end_index]

    keyboard = InlineKeyboardBuilder()
    for product in page_items:
        keyboard.add(
            InlineKeyboardButton(text=product, callback_data=f"product_{product}")
        )
    if page == 0:
        keyboard.adjust(2, 2)
        # Додаємо кнопку "Пошук"
        keyboard.row(InlineKeyboardButton(text="Пошук🔍", callback_data="search_product"))
    else:
        keyboard.adjust(1, 1)
    user = await orm_get_user_by_telegram_id(session, telegram_id)
    if user.status == "creator" and page == 0 and switch and switch_creator:
        keyboard.row(
            InlineKeyboardButton(
                text="Налаштуванян категорії⚙️",
                callback_data=f"settings_category_{category}",
            )
        )

    total_pages = (len(products_list) + items_per_page - 1) // items_per_page
    pagination_buttons = await create_pagination_buttons(page, total_pages, category)

    # Розміщуємо кнопки "Назад" і "Далі" на одному рядку, якщо обидві існують
    if pagination_buttons:
        keyboard.row(*pagination_buttons)

    # Додаємо кнопку "Назад до категорій"
    keyboard.row(
        InlineKeyboardButton(
            text="Назад до категорій⏪", callback_data="back_to_categories"
        )
    )

    return keyboard.as_markup()


async def get_details(session, product):
    description, photo, price, category = await orm_get_product_details(
        session, product
    )
    description = "\nОпис: " + description if description is not None else ""
    text = f"{product}{description}\nЦіна: {price}"
    keyboard = InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Придбати✨", callback_data=f"buy_{product}"),
        InlineKeyboardButton(text="Ввести бажану кількість товару🔢", callback_data=f"few_{product}"),
        InlineKeyboardButton(
            text="Назад до товарів⏪", callback_data=f"back_to_category_{category}"
        ),
    )
    keyboard.adjust(1, 1)
    return text, photo, keyboard.as_markup()


async def trainer_button(session: AsyncSession):  # Блокування показу тренера
    users_id: list[int] = await orm_get_trainers(session)
    keyboard = InlineKeyboardBuilder()
    for user_id in users_id:
        trainer = await orm_get_trainer_full_name(session, user_id)
        if trainer:
            keyboard.add(
                InlineKeyboardButton(
                    text=f"{trainer.first_name} {trainer.last_name}",
                    callback_data=f"choose_{trainer.telegram_id}",
                )
            )
    keyboard.adjust(1, 1)
    keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data="menu_client"))
    return keyboard.as_markup()


async def client_program_button(session, telegram_id, client_telegram_id):
    keyboard = InlineKeyboardBuilder()
    months = [
        "Січень",
        "Лютий",
        "Березень",
        "Квітень",
        "Травень",
        "Червень",
        "Липень",
        "Серпень",
        "Вересень",
        "Жовтень",
        "Листопад",
        "Грудень",
    ]

    current_date = datetime.now()
    # Попередній місяць
    prev_month = current_date - relativedelta(months=1)
    keyboard.add(
        InlineKeyboardButton(
            text=f"{months[prev_month.month - 1]}",
            callback_data=f"program_choose_{prev_month.month}",
        )
    )

    # Поточний місяць
    keyboard.add(
        InlineKeyboardButton(
            text=f"{months[current_date.month - 1]}",
            callback_data=f"program_choose_{current_date.month}",
        )
    )

    # Наступний місяць
    next_month = current_date + relativedelta(months=1)
    keyboard.add(
        InlineKeyboardButton(
            text=f"{months[next_month.month - 1]}",
            callback_data=f"program_choose_{next_month.month}",
        )
    )

    keyboard.adjust(3)  # Розміщуємо кнопки в один стовпець
    user = await orm_get_user_by_telegram_id(session, telegram_id)
    if user.status != 'client':
        keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data=f"client_data_{client_telegram_id}"))

    else:
        keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data="training"))

    return keyboard.as_markup()


async def client_program_month_button(
        session, trainer_telegram_id, client_telegram_id, client_month, switch=False
):
    keyboard = InlineKeyboardBuilder()

    user_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=trainer_telegram_id
    )

    trainer_id = await orm_get_trainer_id_by_user_id(session, user_id=user_id)
    client_id = await orm_get_user_id_by_telegram_id(
        session=session, telegram_id=client_telegram_id
    )

    training_programs = await orm_check_all_training(
        session, trainer_id, client_id, int(client_month)
    )

    # Групуємо дні за тижнями
    weeks = defaultdict(list)
    for day in training_programs:
        day = int(day) if isinstance(day, str) else day
        date = datetime(datetime.now().year, int(client_month), day)
        week_number = date.isocalendar()[1]
        weeks[week_number].append(day)

    # Створюємо кнопки для кожного тижня окремо
    for week, days in sorted(weeks.items()):
        week_buttons = []
        for day in days:
            week_buttons.append(
                InlineKeyboardButton(text=str(day), callback_data=f"view_program_{day}")
            )
        keyboard.row(*week_buttons)
    if switch:
        telegram_id = trainer_telegram_id
    else:
        telegram_id = client_telegram_id
    keyboard.row(
        InlineKeyboardButton(
            text="Назад🔙", callback_data=f"client_program_{telegram_id}"
        )
    )
    return keyboard.as_markup()
