from aiogram.types import CallbackQuery
from aiogram import F, Router

from create_bot import bot, config
from tgbot.kernel.admin.filters import AdminFilter
from tgbot.kernel.admin.inline import AdminWorkersInlineKeyboard
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import WorkersDAO, OrdersDAO

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = AdminWorkersInlineKeyboard()

admin_ids = config.tg_bot.admin_ids


@router.callback_query(F.data == "workers")
async def workers_block(callback: CallbackQuery):
    workers_ids = await RedisConnector.get_role_redis()
    text = "Сотрудники:"
    kb = await inline.workers_list_kb(workers=workers_ids)
    await callback.message.answer(text=text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "worker")
async def workers_block(callback: CallbackQuery):
    worker_id = callback.data.split(":")[1]
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
    kb = inline.delete_worker_kb(worker_id=worker_id)
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "worker_delete")
async def workers_block(callback: CallbackQuery):
    worker_id = callback.data.split(":")[1]
    text = "Воркер уволен"
    kb = inline.home_kb()
    await RedisConnector.delete_role_redis(user_id=worker_id)
    bank_status = {"SBERBANK": "off", "TINKOFF": "off"}
    await WorkersDAO.update(user_id=worker_id, general_status="off", bank_status=bank_status)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)
