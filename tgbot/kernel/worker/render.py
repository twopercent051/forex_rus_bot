from aiogram.utils.markdown import hcode

from create_bot import bot
from tgbot.kernel.worker.inline import WorkerOrderInlineKeyboard

worker_order_inline = WorkerOrderInlineKeyboard()


async def order_worker_render(order: dict, worker_id: str | int):
    text = [
        f"<u>Заявка № {order['id']}</u>\n",
        f"<b>Банк:</b> <i>{order['bank_name']}</i>",
        f"<b>Номер карты:</b> <i>{hcode(order['bank_account'])}</i>",
        f"<b>Сумма к переводу:</b> <i>{order['client_fiat'] / 100} ₽</i>",
        f"<b>Ваша прибыль:</b> <i>{(order['worker_fiat'] - order['client_fiat']) / 100} ₽</i>",
        f"<b>Комментарий:</b> <i>{order['comment']}</i>",
    ]
    kb = worker_order_inline.get_order_kb(order_id=order["id"])
    await bot.send_message(chat_id=worker_id, text="\n".join(text), reply_markup=kb)
