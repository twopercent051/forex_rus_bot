from aiogram.types import CallbackQuery
from aiogram import F, Router

from create_bot import bot, config
from tgbot.kernel.worker.filters import WorkerFilter
from tgbot.kernel.worker.inline import WorkerInlineKeyboard
from tgbot.models.sql_connector import OrdersDAO

router = Router()
router.message.filter(WorkerFilter())
router.callback_query.filter(WorkerFilter())

inline = WorkerInlineKeyboard()

moderator = config.tg_bot.moderator_group


@router.callback_query(F.data == "statistic")
async def statistic_block(callback: CallbackQuery):
    worker_id=str(callback.from_user.id)
    orders = await OrdersDAO.get_many(worker_id=worker_id)
    refuse_count = 0
    finish_count = 0
    finish_total = 0
    for order in orders:
        if worker_id in order["stop_list"]:
            refuse_count += 1
        if order["status"] == "finished":
            finish_count += 1
            finish_total += order["worker_fiat"]
    text = [
        "Статистика сотрудника за последнюю неделю:\n",
        f"<b>Всего ордеров:</b> <i>{len(orders)}</i>",
        f"<b>Отказанных ордеров:</b> <i>{refuse_count}</i>",
        f"<b>Завершённых ордеров:</b> <i>{finish_count}</i>",
        f"<b>Оборот:</b> <i>{finish_total / 100} ₽</i>",
    ]
    kb = inline.home_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)
