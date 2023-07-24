from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from tgbot.kernel.moderator.filters import ModeratorFilter

router = Router()
router.message.filter(ModeratorFilter())
router.callback_query.filter(ModeratorFilter())


def order_moderator_render(order: dict, worker_username: str):
    text = [
        f"<u>Заявка № {order['id']}</u>\n",
        f"<b>Работник:</b> {worker_username}",
        f"<b>Банк:</b> <i>{order['bank_name']}</i>",
        f"<b>Номер карты:</b> <i>{hcode(order['bank_account'])}</i>",
        f"<b>Сумма к переводу:</b> <i>{order['client_fiat'] / 100} ₽</i>",
        f"<b>Ваша прибыль:</b> <i>{(order['worker_fiat'] - order['client_fiat']) / 100} ₽</i>",
        f"<b>Комментарий:</b> <i>{order['comment']}</i>",
    ]
    return "\n".join(text)

