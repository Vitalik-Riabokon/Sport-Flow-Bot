from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from database.func.table_payments import orm_get_last_payment, orm_get_validity_memberships, orm_get_expiration_date, \
    orm_get_count_one_time_training
from database.func.table_products import orm_get_data_by_product_id
from database.func.table_trainer_clients import orm_get_trainer_id
from database.func.table_trainers import orm_get_trainer_details
from database.func.table_users import orm_get_user_id_by_telegram_id, orm_get_user_by_telegram_id

user_memberships_admin_router = Router()


@user_memberships_admin_router.callback_query(lambda c: c.data.startswith("user_memberships_"))
async def user_statistics(callback_query: CallbackQuery, session: AsyncSession):
    client_telegram_id = int(callback_query.data.split("_")[-1])
    user_id = await orm_get_user_id_by_telegram_id(session=session, telegram_id=client_telegram_id)
    check_validity = []
    last_payment = await orm_get_last_payment(session, user_id)

    if last_payment:
        last_product_name, last_product_price, payment_method, payment_date = last_payment
        if payment_method == "cash":
            payment_method = "готівка"
        else:
            payment_method = "карта"
    else:
        last_product_name, last_product_price, payment_method, payment_date = (
            "Особа нічого не купувала",
            "",
            "",
            "",
        )

    trainer_id = await orm_get_trainer_id(session=session, client_id=user_id)
    if trainer_id:
        data_trainer = await orm_get_trainer_details(session, trainer_id)
        trainer_first_name = data_trainer[0]['first_name']
        trainer_last_name = data_trainer[0]['last_name']
    else:
        trainer_first_name, trainer_last_name = "Не має тренера", ""

    for user in await orm_get_validity_memberships(session):
        if client_telegram_id in user:
            check_validity.append(user)
            break
    data_end_subscription = await orm_get_expiration_date(session, user_id)
    if check_validity or data_end_subscription:
        user = await orm_get_user_by_telegram_id(session, client_telegram_id)
        if data_end_subscription:

            product_id, payment_date, expiration_date = data_end_subscription
            product_name, product_price = await orm_get_data_by_product_id(
                session, product_id
            )
        else:
            user = await orm_get_user_by_telegram_id(session, client_telegram_id)
            _, _, _, _, product_name, product_price, payment_date, expiration_date = check_validity[0]
        await callback_query.message.edit_text(
            text=f"Ініціали: {user.first_name} {user.last_name}\n"
                 f"Номер телефону: {user.phone_number}\n"
                 f"Початок: {payment_date}\nКінець: {expiration_date}\n"
                 f"Абонимент: {product_name} - {product_price}\n"
                 f"Тренер: {trainer_first_name} {trainer_last_name}\n\n"
                 f"Остання купівля: {last_product_name} - {last_product_price} {payment_method}\n"
                 f"Дата купування: {payment_date} ",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Назад🔙", callback_data=f"all_clients")]
                ]
            ),
        )
    else:
        data = await orm_get_count_one_time_training(session, user_id)
        if data:
            count_visiting, sum_price = data
            if count_visiting == 0 or sum_price is None:
                count_visiting, sum_price = "Не має даних", "Не має даних"
        else:
            count_visiting, sum_price = "Не має даних", "Не має даних"

        await callback_query.message.edit_text(
            "Користувач не має абонименту\n"
            f"Місячний дохід для залу: {sum_price}\n"
            f"Місячна кількість відвідування: {count_visiting}\n\n"
            f"Остання купівля: {last_product_name} - {last_product_price} {payment_method}\n"
            f"Дата купування: {payment_date} ",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад🔙",
                            callback_data=f"user_data_{client_telegram_id}",
                        )
                    ]
                ]
            ),
        )
