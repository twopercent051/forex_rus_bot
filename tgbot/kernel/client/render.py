import time

from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.kernel.client.inline import ClientInlineKeyboard, ClientOrderInlineKeyboard
from tgbot.misc.fiat import fiat_calc
from tgbot.misc.states import ClientFSM
from tgbot.services.garantex import GarantexAPI
from tgbot.services.scheduler import CreateTask

client_inline = ClientInlineKeyboard()
client_order_inline = ClientOrderInlineKeyboard()


async def main_menu_render(user_id: int | str, start: bool):
    if start:
        text = "Добро пожаловать в ForexRub. Здесь вы можете быстро обменять USDT в рубль переводом на карту " \
               "Сбербанка или Тинькофф. Просто создайте заявку. Если у вас возникнут какие-либо вопросы смело пишите " \
               "в поддержку, ответим в ближайшее время"
    else:
        text = "Главное меню"
    kb = client_inline.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


async def order_render(user_id: str | int, state: FSMContext):
    state_data = await state.get_data()
    market_currency = await GarantexAPI.get_currency()
    market_fiat = state_data['coin_value'] * market_currency / 100
    client_currency = fiat_calc(market_fiat=market_currency)
    fiat_calc_dict = fiat_calc(market_fiat=market_fiat)
    await state.update_data(currency=market_currency,
                            client_fiat=fiat_calc_dict["client_fiat"],
                            worker_fiat=fiat_calc_dict["worker_fiat"],
                            profit_fiat=fiat_calc_dict["profit_fiat"])
    text = [
        "Проверьте введённые данные и подтвердите заявку:\n",
        f"<b>Валюта к обмену:</b> <i>{state_data['coin']}</i>",
        f"<b>Сумма к обмену:</b> <i>{state_data['coin_value'] / 100}</i>",
        f"<b>Обменный курс:</b> <i>{client_currency['client_fiat'] / 100}</i>",
        f"<b>Сумма к получению:</b> <i>{fiat_calc_dict['client_fiat'] / 100} ₽</i>",
        f"<b>Банк:</b> <i>{state_data['bank_name']}</i>",
        f"<b>Реквизиты:</b> <i>{state_data['bank_account']}</i>",
        f"<b>Комментарий:</b> <i>{state_data['comment']}</i>\n",
        "<u>Подтвердите заявку в течении 10 минут</u>"
    ]
    task_id = f"{user_id}_{int(time.time())}"
    kb = client_order_inline.accept_order_kb(task_id=task_id)
    msg = await bot.send_message(chat_id=user_id, text="\n".join(text), reply_markup=kb)
    await state.set_state(ClientFSM.home)
    await CreateTask.delete_order(user_id=user_id, message_id=msg.message_id, task_id=task_id)
