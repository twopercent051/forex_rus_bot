from datetime import datetime, timedelta

from create_bot import scheduler, bot, config
from tgbot.kernel.client.inline import InlineKeyboard
from tgbot.models.sql_connector import OrdersDAO, CryptoAccountsDAO
from tgbot.services.garantex import GarantexAPI

admin_ids = config.tg_bot.admin_ids

inline = InlineKeyboard()


class Functions:

    @classmethod
    async def update_jwt(cls):
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

    @classmethod
    async def delete_order_func(cls, user_id: int | str, message_id: str | int):
        text = "⚠️ Заявка больше не актуальная. Создайте новую"
        kb = inline.home_kb()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=kb)
        await bot.send_message(chat_id=user_id, text=text)

    @classmethod
    async def cancel_order_func(cls, user_id: int | str, message_id: str, order_id: int):
        text = f"⚠️ Заявка # {order_id} больше не актуальная. Создайте новую"
        kb = inline.home_kb()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=kb)
        await bot.send_message(chat_id=user_id, text=text)
        await OrdersDAO.update(order_id=order_id, status="cancelled")


class CreateTask:

    @classmethod
    async def update_jwt(cls):
        scheduler.add_job(
            func=Functions.update_jwt,
            trigger="cron",
            hour=1,
        )

    @classmethod
    async def delete_order(cls, user_id: int | str, message_id: str | int, task_id: str):
        dtime = datetime.utcnow() + timedelta(minutes=10)
        scheduler.add_job(
            id=task_id,
            func=Functions.delete_order_func,
            trigger="date",
            next_run_time=dtime,
            kwargs={
                "user_id": user_id,
                "message_id": message_id,
            }
        )

    @classmethod
    async def cancel_order(cls, user_id: int | str, message_id: str, order_id: int, task_id: str):
        dtime = datetime.utcnow() + timedelta(minutes=20)
        scheduler.add_job(
            id=task_id,
            func=Functions.cancel_order_func,
            trigger="date",
            next_run_time=dtime,
            kwargs={
                "user_id": user_id,
                "message_id": message_id,
                "order_id": order_id,
            }
        )

    @classmethod
    async def delete_task(cls, task_id: str):
        scheduler.remove_job(job_id=task_id)
