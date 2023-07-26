from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.kernel.admin.inline import AdminInlineKeyboard
from tgbot.misc.states import AdminFSM
from tgbot.models.sql_connector import OrdersDAO

inline = AdminInlineKeyboard()


async def main_menu_render(user_id: int | str, start: bool, state: FSMContext):
    text = "Добро пожаловать в клуб. Вы вошли как СУПЕРПОЛЬЗОВАТЕЛЬ" if start else "ГЛАВНОЕ МЕНЮ"
    kb = inline.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


async def week_statistic_render(user_id: int | str):
    orders = await OrdersDAO.get_many()
    finish_count = 0
    total_coin_value = 0
    total_profit_value = 0
    for order in orders:
        if order["status"] == "finished":
            finish_count += 1
            total_coin_value += order["coin_value"]
            total_profit_value += order["profit_fiat"]
    text = [
        "Статистика за последнюю неделю:\n",
        f"<b>Всего ордеров:</b> <i>{len(orders)}</i>",
        f"<b>Завершённых ордеров:</b> <i>{finish_count}</i>",
        f"<b>Оборот USDT:</b> <i>{total_coin_value / 100}</i>",
        f"<b>Прибыль:</b> <i>{total_profit_value / 100} ₽</i>",
    ]
    kb = inline.home_kb()
    await bot.send_message(chat_id=user_id, text="\n".join(text), reply_markup=kb)
