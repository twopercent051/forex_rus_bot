from datetime import datetime, timedelta

from create_bot import scheduler, bot, config
from tgbot.kernel.admin.render import week_statistic_render
from tgbot.kernel.client.inline import ClientInlineKeyboard
from tgbot.kernel.worker.inline import WorkerOrderInlineKeyboard
from tgbot.kernel.worker.render import order_worker_render
from tgbot.models.sql_connector import OrdersDAO, CryptoAccountsDAO, WorkersDAO
from tgbot.services.garantex import GarantexAPI

admin_ids = config.tg_bot.admin_ids
moderator = config.tg_bot.moderator_group

client_inline = ClientInlineKeyboard()
worker_order_inline = WorkerOrderInlineKeyboard()


class Functions:

    @staticmethod
    async def update_jwt():
        accounts = await CryptoAccountsDAO.get_many()
        for account in accounts:
            uid = GarantexAPI.decrypt(data=account["uid"])
            private_key = GarantexAPI.decrypt(data=account["private_key"])
            jwt = GarantexAPI.update_jwt(uid=uid, private_key=private_key)
            if jwt:
                jwt = GarantexAPI.encrypt(data=jwt)
                await CryptoAccountsDAO.update(account_id=account["id"], jwt=jwt)
            else:
                await CryptoAccountsDAO.update(account_id=account["id"], status="off")
                for admin in admin_ids:
                    text = f"⚠️ НЕ УДАЛОСЬ ОБНОВИТЬ ТОКЕН АККАУНТА {account['title']}"
                    await bot.send_message(chat_id=admin, text=text)

    @staticmethod
    async def weekly_task_func():
        await WorkersDAO.reset_total_month()
        for admin in admin_ids:
            await week_statistic_render(user_id=admin)

    @staticmethod
    async def delete_order_func(user_id: int | str, message_id: str | int):
        text = "⚠️ Заявка больше не актуальная. Создайте новую"
        kb = client_inline.home_kb()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=kb)
        await bot.send_message(chat_id=user_id, text=text)

    @staticmethod
    async def cancel_order_func(user_id: int | str, message_id: str, order_id: int):
        text = f"⚠️ Заявка # {order_id} больше не актуальная. Создайте новую"
        kb = client_inline.home_kb()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=kb)
        await bot.send_message(chat_id=user_id, text=text)
        await OrdersDAO.update(order_id=order_id, status="cancelled")

    @staticmethod
    async def remind_worker_order_func(user_id: int | str, order_id: int):
        text = f"⚠️ Вы приняли в работу ордер № {order_id} но до сих пор её не завершили!"
        kb = worker_order_inline.refuse_order_kb(order_id=order_id)
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)

    @staticmethod
    async def cancel_worker_order_func(user_id: int | str, order_id: int, remind_task_id: str):
        text = f"📛 Мы передали ордер № {order_id} другому сотруднику"
        order = await OrdersDAO.get_one_or_none(order_id=order_id)
        stop_list: list = order["stop_list"]
        stop_list.append(str(user_id))
        free_worker = await WorkersDAO.get_free(stop_list=stop_list)
        if len(free_worker) == 0:
            mod_text = f"⚠️ На заявку № {order_id} не удалось найти отправителя"
            await bot.send_message(chat_id=moderator, text=mod_text)
        else:
            await order_worker_render(order=order, worker_id=free_worker[0]["user_id"])
        await CreateTask.delete_task(task_id=remind_task_id)
        await bot.send_message(chat_id=user_id, text=text)


class CreateTask:

    @classmethod
    async def start_scheduler(cls):
        await cls.update_jwt()
        await cls.update_jwt()
        await Functions.update_jwt()

    @staticmethod
    async def update_jwt():
        scheduler.add_job(func=Functions.update_jwt,
                          trigger="interval",
                          hours=12)

    @staticmethod
    async def weekly_task():
        scheduler.add_job(func=Functions.weekly_task_func,
                          trigger="cron",
                          day_of_week="mon")

    @staticmethod
    async def delete_order(user_id: int | str, message_id: str | int, task_id: str):
        dtime = datetime.utcnow() + timedelta(minutes=10)
        scheduler.add_job(id=task_id,
                          func=Functions.delete_order_func,
                          trigger="date",
                          next_run_time=dtime,
                          kwargs=dict(user_id=user_id,
                                      message_id=message_id))

    @staticmethod
    async def cancel_order(user_id: int | str, message_id: str, order_id: int, task_id: str):
        dtime = datetime.utcnow() + timedelta(minutes=20)
        scheduler.add_job(id=task_id,
                          func=Functions.cancel_order_func,
                          trigger="date",
                          next_run_time=dtime,
                          kwargs=dict(user_id=user_id,
                                      message_id=message_id,
                                      order_id=order_id))

    @staticmethod
    async def remind_worker_order(user_id: int | str, order_id: int, task_id: str):
        scheduler.add_job(id=task_id,
                          func=Functions.remind_worker_order_func,
                          trigger="interval",
                          minutes=5,
                          kwargs=dict(user_id=user_id,
                                      order_id=order_id))

    @staticmethod
    async def cancel_worker_order(user_id: int | str, order_id: int, task_id: str, remind_task_id: str):
        dtime = datetime.utcnow() + timedelta(minutes=22)
        scheduler.add_job(id=task_id,
                          func=Functions.remind_worker_order_func,
                          trigger="date",
                          next_run_time=dtime,
                          kwargs=dict(user_id=user_id,
                                      order_id=order_id,
                                      remind_task_id=remind_task_id))

    @staticmethod
    async def delete_task(task_id: str):
        scheduler.remove_job(job_id=task_id)
