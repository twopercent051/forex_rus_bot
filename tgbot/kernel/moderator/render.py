from aiogram.utils.markdown import hcode

from create_bot import bot, config
from tgbot.kernel.moderator.inline import ModeratorOrderInlineKeyboard
from tgbot.models.sql_connector import WorkersDAO, OrdersDAO
from tgbot.services.garantex import GarantexAPI

order_inline = ModeratorOrderInlineKeyboard()

admin_ids = config.tg_bot.admin_ids


async def main_menu_render(moderator_id: int | str):
    text = "ГЛАВНОЕ МЕНЮ"
    kb = order_inline.main_menu_kb()
    await bot.send_message(chat_id=moderator_id, text=text, reply_markup=kb)


def order_moderator_render(order: dict, worker_username: str) -> str:
    text = [
        f"<u>Заявка № {order['id']}</u>\n",
        f"<b>Работник:</b> {worker_username}",
        f"<b>Банк:</b> <i>{order['bank_name']}</i>",
        f"<b>Номер карты:</b> <i>{hcode(order['bank_account'])}</i>",
        f"<b>Сумма к переводу:</b> <i>{order['client_fiat'] / 100} ₽</i>",
        f"<b>Комментарий:</b> <i>{order['comment']}</i>",
    ]
    return "\n".join(text)


async def full_order_profile(order: dict, user_id: int | str):
    if order["worker_id"] == "---" or order["worker_id"] is None:
        worker_username = "---"
    else:
        worker = await WorkersDAO.get_one_or_none(user_id=order["worker_id"])
        worker_username = worker["username"]
    moderator = order["moderator_id"] if order["moderator_id"] else "---"
    text = [
        f"<u>Заявка № {order['id']}</u>\n",
        f"<b>Клиент:</b> <i>{order['client_username']}</i>",
        f"<b>Объём USDT:</b> <i>{order['coin_value'] / 100}</i>",
        f"<b>Курс обмена:</b> <i>{order['currency'] / 100}</i>",
        f"<b>Банк:</b> <i>{order['bank_name']}</i>",
        f"<b>Номер карты:</b> <i>{hcode(order['bank_account'])}</i>",
        f"<b>Сумма к переводу клиенту:</b> <i>{order['client_fiat'] / 100} ₽</i>",
        f"<b>Сумма к переводу воркеру:</b> <i>{order['worker_fiat'] / 100} ₽</i>",
        f"<b>Крипто-аккаунт:</b> <i>{order['crypto_account']['title']}</i>",
        f"<b>Комментарий:</b> <i>{order['comment']}</i>",
        f"<b>Воркер:</b> <i>{worker_username}</i>",
        f"<b>Модератор:</b> <i>{moderator}</i>",
        f"<b>Статус:</b> <i>{order['status'].upper()}</i>",
    ]
    kb = order_inline.order_profile_kb(order=order)
    if order["document_id"]:
        await bot.send_document(chat_id=user_id,
                                document=order["document_id"],
                                caption="\n".join(text),
                                reply_markup=kb)
        return
    await bot.send_message(chat_id=user_id, text="\n".join(text), reply_markup=kb)


async def order_finish_render(order: dict, moderator_id: str | int):
    garantex_code = await GarantexAPI.create_garantex_code(account_id=order["crypto_account"]["id"],
                                                           amount=order["worker_fiat"])
    if garantex_code[1] == 200:
        worker_text = f"Ваш код Garantex по ордеру № {order['id']}:\n<spoiler>{hcode(garantex_code[0])}</spoiler>"
        await bot.send_message(chat_id=int(order["worker_id"]), text=worker_text)
    else:
        for admin in admin_ids:
            admin_text = f"По ордеру № {order['id']} не удалось сформировать код Garantex\n{garantex_code[0]}"
            await bot.send_message(chat_id=admin, text=admin_text)
    await OrdersDAO.update(order_id=order['id'], status="finished", moderator_id=str(moderator_id))
    await WorkersDAO.update_total_month(worker_id=order["worker_id"], value=order["worker_fiat"])
    client_text = f"По заказу № {order['id']} выплата проведена"
    await bot.send_document(chat_id=order["client_id"], document=order["document_id"], caption=client_text)
