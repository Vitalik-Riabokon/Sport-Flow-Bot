from aiogram import Router

from handlers.group_chat.user_group import user_group_router
from handlers.privat_chat.admins_menu.admin_menu import admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.all_clients_admin_menu.all_client_admin_menu import \
    all_client_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.all_clients_admin_menu.search_client_admin_menu import \
    search_client_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.all_clients_admin_menu.user_data_admin_menu import \
    user_data_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.all_clients_admin_menu.user_memberships_admin_menu import \
    user_memberships_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.all_clients_admin_menu.validity_memberships_admin_menu import \
    validity_memberships_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.client_adlmin_menu import client_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.check_program_menu import \
    check_program_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.client_membres_admin_menu import \
    client_members_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.client_program_admin_menu import \
    client_program_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.coach_yes_admin_menu import \
    coach_yes_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.delete_clients_admin_menu.delete_client_admin_menu import \
    delete_client_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.delete_clients_admin_menu.delete_successfully_admin_menu import \
    delete_successfully_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.month_day_admin_menu import \
    month_day_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.my_client_admin_menu import \
    my_client_admin_router
from handlers.privat_chat.admins_menu.clients_admin_menu.my_clients_admin_menu.training_client_program_admin_menu import \
    training_client_program_admin_router
from handlers.privat_chat.admins_menu.open_close_menu.open_close_admin_menu import open_close_admin_router
from handlers.privat_chat.admins_menu.qr_code.qr_cod_admin_menu import qr_code_admin_router
from handlers.privat_chat.clients_menu.audit_buy_client_menu import audit_buy_client_router
from handlers.privat_chat.clients_menu.client_menu import client_router
from handlers.privat_chat.clients_menu.goods_user_menu import goods_client_router
from handlers.privat_chat.clients_menu.membership_client_menu import membership_client_router
from handlers.privat_chat.clients_menu.one_time_training_client_menu import one_time_training_client_router
from handlers.privat_chat.clients_menu.program_client_menu import program_client_router
from handlers.privat_chat.clients_menu.schedule_client_menu import schedule_router
from handlers.privat_chat.clients_menu.search_product_client_menu import search_product_client_router
from handlers.privat_chat.clients_menu.session_client_menu import session_client_router
from handlers.privat_chat.clients_menu.trainer_client_menu import trainer_client_router
from handlers.privat_chat.clients_menu.training_client_menu import training_client_router
from handlers.privat_chat.command_menu.command_menu_menu import menu_router
from handlers.privat_chat.command_menu.command_start_menu import start_router
from handlers.privat_chat.command_menu.delete_other_messeg import delete_message_router
from handlers.privat_chat.creators_menu.creator_menu import creator_router
from handlers.privat_chat.creators_menu.redact_creator.redact_creator_menu import redact_creator_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.add_new_category_menu import \
    add_category_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.add_new_product_menu import \
    add_product_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.category_settings_menu import \
    category_settings_creator_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.change_category_name_menu import \
    change_category_name_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.delete_creator_menu.delete_category_menu import \
    delete_category_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.delete_creator_menu.delete_product_menu import \
    delete_product_router
from handlers.privat_chat.creators_menu.redact_creator.redact_goods_creator.redact_goods_creator_menu import \
    redact_goods_creator_router
from handlers.privat_chat.creators_menu.redact_creator.redact_gym_creator.redact_gym_membership_menu import \
    redact_membership_router
from handlers.privat_chat.creators_menu.redact_creator.redact_gym_creator.redact_gym_menu import redact_gym_router
from handlers.privat_chat.creators_menu.redact_creator.redact_gym_creator.redact_gym_one_time_training_menu import \
    redact_one_time_training_router
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.cash_day_menu import cash_day_router
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.creator_admin_statistic_menu import \
    statistic_router
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.details_day_month_menu.creator_details_day_month import \
    detail_day_month_router
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.details_day_month_menu.detail_day_menu import \
    detail_day_router
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.details_day_month_menu.detail_month_menu import \
    detail_month_router
from handlers.privat_chat.creators_menu.statistic_admin_creator_menu.statistic_creator_menu import \
    creator_statistic_router
from handlers.privat_chat.entry_menu.audit_log_menu import audit_log_menu_router
from handlers.privat_chat.entry_menu.log_menu import login_router
from handlers.privat_chat.registration_menu.audit_reg_menu import audit_reg_menu_router
from handlers.privat_chat.registration_menu.reg_menu import reg_router


async def activate_router() -> list[Router]:
    routers = [
        reg_router, login_router, user_group_router, audit_log_menu_router,
        audit_reg_menu_router, start_router, menu_router, delete_message_router,

        client_router, training_client_router, schedule_router,
        one_time_training_client_router, membership_client_router, audit_buy_client_router, trainer_client_router,
        search_product_client_router, session_client_router, program_client_router, goods_client_router,

        admin_router, client_admin_router, my_client_admin_router, client_members_admin_router, coach_yes_admin_router,
        training_client_program_admin_router, delete_client_admin_router, client_program_admin_router,
        delete_successfully_admin_router, all_client_admin_router, validity_memberships_admin_router,
        user_data_admin_router, user_memberships_admin_router, qr_code_admin_router, open_close_admin_router,
        month_day_admin_router, check_program_admin_router, search_client_admin_router,

        creator_router, redact_creator_router, redact_gym_router, redact_membership_router,
        redact_one_time_training_router, detail_day_router, detail_day_month_router, detail_month_router,
        redact_goods_creator_router, delete_product_router, statistic_router, creator_statistic_router,
        cash_day_router, delete_category_router, category_settings_creator_router, add_category_router,
        add_product_router, change_category_name_router,

    ]
    return routers
