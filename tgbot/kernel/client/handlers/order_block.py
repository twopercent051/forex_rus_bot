import time

from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from create_bot import bot, config
from tgbot.kernel.client.inline import ClientOrderInlineKeyboard
from tgbot.kernel.client.render import order_render
from tgbot.kernel.worker.handlers.order_block import order_worker_render
from tgbot.misc.states import ClientFSM
from tgbot.models.sql_connector import CryptoAccountsDAO, WorkersDAO, OrdersDAO
from tgbot.misc.fiat import fiat_calc
from tgbot.services.garantex import GarantexAPI
from tgbot.services.scheduler import CreateTask
from tgbot.misc.workers import Workers

router = Router()

inline = ClientOrderInlineKeyboard()

moderator = config.tg_bot.moderator_group


@router.callback_query(F.data.split(":")[0] == "order")
async def order_block(callback: CallbackQuery):
    if callback.data.split(":")[1] == "new":
        free_accounts = await CryptoAccountsDAO.get_many(status="on")
        if len(free_accounts) == 0:
            text = "К сожалению, сейчас у нас нет возможности сделать перевод, попробуйте позднее или напишите нам в " \
                   "поддержку"
            kb = inline.home_kb()
        else:
            text = "Выберите банк, на который желаете получить перевод"
            kb = inline.banks_kb()
    else:  # История транзакций
        client_id = str(callback.from_user.id)
        orders = await OrdersDAO.get_many(client_id=client_id)
        total_coin_value = 0
        total_fiat_value = 0
        active_orders = []
        for order in orders:
            if order["status"] == "finished":
                total_coin_value += order["coin_value"]
                total_fiat_value += order["client_fiat"]
            else:
                active_orders.append(order)
        text = [
            "Ваша статистика:\n",
            f"<b>Всего ордеров:</b> <i>{len(orders)}</i>",
            f"<b>Объём USDT:</b> <i>{total_coin_value / 100}</i>",
            f"<b>Полученная сумма:</b> <i>{total_fiat_value / 100} ₽</i>",
            f"<b>Завершённых ордеров:</b> <i>{len(orders) - len(active_orders)}</i>",
        ]
        if len(active_orders) > 0:
            text.append(f"Незавершённые ордера:\n{'-' * 15}")
        kb = inline.orders_history_kb(orders=active_orders)
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "bank")
async def order_block(callback: CallbackQuery, state: FSMContext):
    bank = callback.data.split(":")[1]
    workers = await WorkersDAO.get_many()
    free_workers = Workers.check_bank(workers=workers, bank=bank)
    if len(free_workers) == 0:
        text = "В настоящий момент нет предложения на обмен в этот банк. Выберите другой банк или попробуйте позднее"
    else:
        currency = await GarantexAPI.get_currency()
        client_currency = fiat_calc(market_fiat=currency)["client_fiat"]
        text = f"В настоящий момент обменный курс составляет <i>{client_currency / 100}</i>. Введите объём в USDT, " \
               f"который хотите обменять. Число округляется до двух знаков после запятой"
        await state.update_data(bank_name=bank)
        await state.set_state(ClientFSM.coin_value)
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, ClientFSM.coin_value)
async def order_block(message: Message, state: FSMContext):
    try:
        coin_value = int(float(message.text.replace(",", ".")) * 100)
    except ValueError:
        text = "Введите число (разделитель точка или запятая). Число округляется до двух знаков после запятой"
        await message.answer(text)
        return
    text = "Укажите номер карты, на которую хотите получить перевод. Номер указан на лицевой стороне карты и состоит " \
           "из 16 цифр.\n\n<b>Внимание!\nНаши сотрудники никогда не запрашивают CVV-код с оборотной стороны карты " \
           "либо смс-коды. Если вы столкнулись с такими случаями, это мошенники</b>"
    kb = inline.home_kb()
    await state.update_data(coin_value=coin_value)
    await state.set_state(ClientFSM.bank_account)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, ClientFSM.bank_account)
async def order_block(message: Message, state: FSMContext):
    text = "Введите комментарий если требуется"
    kb = inline.pass_comment_kb()
    await state.update_data(bank_account=message.text, coin="USDT")
    await state.set_state(ClientFSM.comment)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, ClientFSM.comment)
async def order_block(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await order_render(user_id=message.from_user.id, state=state)


@router.callback_query(F.data == "pass_comment")
async def order_block(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="---")
    await order_render(user_id=callback.from_user.id, state=state)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "accept_order")
async def order_block(callback: CallbackQuery, state: FSMContext):
    task_id = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)
    crypto_account = await CryptoAccountsDAO.get_one_by_processes()
    wallet = await GarantexAPI.get_wallet(account_id=crypto_account["id"])
    await CreateTask.delete_task(task_id=task_id)
    state_data = await state.get_data()
    client_username = f"@{callback.from_user.username}" if callback.from_user.username else "---"
    order = await OrdersDAO.create_returning(client_id=user_id,
                                             client_username=client_username,
                                             coin=state_data["coin"],
                                             coin_value=state_data["coin_value"],
                                             currency=state_data["currency"],
                                             client_fiat=state_data["client_fiat"],
                                             worker_fiat=state_data["worker_fiat"],
                                             profit_fiat=state_data["profit_fiat"],
                                             bank_name=state_data["bank_name"],
                                             bank_account=state_data["bank_account"],
                                             crypto_account={"id": crypto_account["id"],
                                                             "title": crypto_account["title"]},
                                             comment=state_data["comment"],
                                             worker_id="---")
    await CryptoAccountsDAO.update_processes(account_id=crypto_account["id"], value=1)
    task_id = f"{user_id}_{int(time.time())}"
    text = f"Ордер # {order['id']} создан.\n\n{hcode(wallet['address'])}\nСеть ERC20\n\nПереведите USDT на указанный " \
           f"кошелёк. Время жизни заявки составляет 20 минут. По истечении этого времени заявка будет " \
           f"отменена.\n\n<u>Внимание! Убедитесь, что вы выбрали верный адрес и сеть для перевода. При переводе на " \
           f"неверный реквизиты ваши средства будут утеряны!</u>"
    kb = inline.order_paid_kb(order_id=order["id"], task_id=task_id)
    msg = await callback.message.answer(text, reply_markup=kb)
    await CreateTask.cancel_order(user_id=user_id, message_id=msg.message_id, order_id=order["id"], task_id=task_id)


@router.callback_query(F.data.split(":")[0] == "cancel_order")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    task_id = int(callback.data.split(":")[2])
    text = f"Ордер # {order_id} отменён"
    kb = inline.home_kb()
    await CreateTask.delete_task(task_id=task_id)
    await OrdersDAO.update(order_id=order_id, status="cancelled")
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "paid")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    task_id = callback.data.split(":")[2]
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order["status"] in ["paid_client", "paid_worker"]:
        text = "Мы уже обрабатываем заявку"
        await callback.message.answer(text)
        return
    if order["status"] in ["finished", "cancelled"]:
        text = "Заявка завершена"
        await callback.message.answer(text)
        return
    if order["status"] == "created":
        account_id = order["crypto_account"]["id"]
        start_time = order["dtime"]
        coin_value = order["coin_value"]
        payment_status = await GarantexAPI.get_deposit_history(account_id=account_id,
                                                               start_time=start_time,
                                                               coin_value=coin_value)
        if payment_status:
        # if True:
            text = "✅ Мы получили перевод. Ожидайте, в ближайшее время вы получите перевод на банковский счёт."
            kb = inline.home_kb()
            if order["worker_id"] is None or order["worker_id"] == "---":
                free_worker = await WorkersDAO.get_free(bank=order["bank_name"])
                if len(free_worker) == 0:
                    mod_text = f"⚠️ На заявку № {order_id} не удалось найти отправителя"
                    await bot.send_message(chat_id=moderator, text=mod_text)
                else:
                    await order_worker_render(order=order, worker_id=free_worker[0]["user_id"])
            await CryptoAccountsDAO.update_processes(account_id=account_id, value=-1)
            await OrdersDAO.update(order_id=order_id, status="paid_client")
            error_market = await GarantexAPI.usdt_to_rub_market(account_id=int(account_id))
            if error_market:
                admin_ids = config.tg_bot.admin_ids
                for admin in admin_ids:
                    text_admin = f"По ордеру {order_id} не удалось перевести USDT в RUB\n{error_market}"
                    await bot.send_message(chat_id=admin, text=text_admin)
        else:
            text = "Мы пока не получили перевод. Попробуйте ещё раз позднее. Не переживайте, если в течении 30 минут " \
                   "статус не изменится смело пишите в поддержку"
            kb = inline.order_paid_kb(order_id=order["id"], task_id=task_id)
        await CreateTask.delete_task(task_id=task_id)
        await callback.message.answer(text, reply_markup=kb)
        await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "order_profile")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order is None:
        return
    wallet = await GarantexAPI.get_wallet(account_id=int(order["crypto_account"]["id"]))
    text = [
        f"<u>Заявка № {order['id']}</u>\n",
        f"<b>Объём USDT:</b> <i>{order['coin_value'] / 100}</i>",
        f"<b>Курс обмена:</b> <i>{order['currency'] / 100}</i>",
        f"<b>Банк:</b> <i>{order['bank_name']}</i>",
        f"<b>Номер карты:</b> <i>{hcode(order['bank_account'])}</i>",
        f"<b>Сумма к переводу клиенту:</b> <i>{order['client_fiat'] / 100} ₽</i>",
        f"<b>Крипто-аккаунт:</b> <i>{hcode(wallet['address'])}</i>",
        f"<b>Комментарий:</b> <i>{order['comment']}</i>",
    ]
    kb = inline.support_order_kb()
    if order["document_id"]:
        await callback.message.answer_document(document=order["document_id"], caption="\n".join(text), reply_markup=kb)
        return
    await callback.message.answer(text="\n".join(text), reply_markup=kb)
