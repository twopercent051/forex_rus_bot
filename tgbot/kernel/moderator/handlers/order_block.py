import asyncio
import os

from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from create_bot import bot, config
from tgbot.kernel.moderator.filters import ModeratorFilter
from tgbot.kernel.moderator.inline import ModeratorOrderInlineKeyboard
from tgbot.kernel.moderator.render import full_order_profile, order_finish_render
from tgbot.kernel.worker.render import order_worker_render
from tgbot.misc.states import ModeratorFSM
from tgbot.models.sql_connector import OrdersDAO, WorkersDAO
from tgbot.services.excel import create_excel

router = Router()
router.message.filter(ModeratorFilter())
router.callback_query.filter(ModeratorFilter())

admin_ids = config.tg_bot.admin_ids
moderator = config.tg_bot.moderator_group

inline = ModeratorOrderInlineKeyboard()


@router.callback_query(F.data.split(":")[0] == "moderation_order")
async def order_block(callback: CallbackQuery, state: FSMContext):
    decision = callback.data.split(":")[1]
    order_id = int(callback.data.split(":")[2])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    worker_id = order["worker_id"]
    if decision == "accept":
        text = f"Ордер {order_id} завершён. Средства отправлены воркеру, чек клиенту"
        await order_finish_render(order=order, moderator_id=callback.from_user.id)
    else:  # refuse
        text = f"Укажите причину отказа для волкера. Дальнейшая модерация заявки через Главное меню -> Поиск по ID. " \
               f"ID ордера {hcode(order_id)}"
        await state.set_state(ModeratorFSM.refuse_comment)
        await state.update_data(order_id=order_id, worker_id=worker_id)
        await OrdersDAO.update(order_id=order_id, status="refused")
    await callback.message.answer(text)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, ModeratorFSM.refuse_comment)
async def order_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    order_id = state_data["order_id"]
    worker_id = state_data["worker_id"]
    worker_text = f"❗️<u>Модератор отклонил ваш чек по ордеру № {order_id}</u>\n\n{message.text}\n"
    worker_kb = inline.answer_kb(sender_id=moderator)
    moderator_text = "Сообщение отправлено"
    await state.set_state(ModeratorFSM.home)
    await bot.send_message(chat_id=worker_id, text=worker_text, reply_markup=worker_kb)
    await message.answer(text=moderator_text)


@router.callback_query(F.data == "orders")
async def order_block(callback: CallbackQuery):
    text = "Меню ордеров"
    kb = inline.orders_menu_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "active_orders")
async def order_block(callback: CallbackQuery):
    active_orders = await OrdersDAO.get_active()
    text = "Активные ордера"
    kb = inline.orders_list_kb(orders=active_orders)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "order_profile")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    await full_order_profile(order=order, user_id=moderator)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "set_workers")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order is None:
        return
    if order["status"] == "created":
        text = "⚠️ ⚠️Сейчас клиент не перевёл USDT на крипто-аккаунт. Ручное назначение воркера будет означать, " \
               "что вы получили перевод и по окончании ордера воркеру будет отправлен код Garantex"
        await callback.message.answer(text)
        await asyncio.sleep(2)
    free_workers = await WorkersDAO.get_free(bank=order["bank_name"])
    text = "Выберите воркера. Он будет немедленно назначен на ордер"
    kb = inline.workers_list_kb(workers=free_workers, order_id=order_id)
    await callback.message.answer(text=text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "set_worker")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    worker_id = callback.data.split(":")[2]
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order is None:
        return
    worker = await WorkersDAO.get_one_or_none(user_id=worker_id)
    if order["status"] == "created":
        await OrdersDAO.update(order_id=order_id, status="paid_client", worker_id=worker_id)
    else:
        await OrdersDAO.update(order_id=order_id, worker_id=worker_id)
    await order_worker_render(order=order, worker_id=worker_id)
    text = f"Воркер {worker['username']} назначен на заказ {order_id}"
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "finish_order")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order["document_id"]:
        text = "Данное действие отметит заказ как завершённый, клиент получит квитанцию об оплате, а воркер " \
               "код Garantex"
        kb = inline.finish_order_kb(order_id=order_id)
    else:
        text = "Чтобы заверить ордер, необходимо к нему прикрепить чек об оплате"
        kb = inline.set_check_kb(order_id=order_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F. data.split(":")[0] == "finish_order_accept")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order is None:
        return
    await order_finish_render(order=order, moderator_id=callback.from_user.id)
    text = f"👍 Ордер № {order_id} завершён"
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "set_check")
async def order_block(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(":")[1])
    text = "Загрузите актуальный чек"
    kb = inline.home_kb()
    await state.set_state(ModeratorFSM.check)
    await state.update_data(order_id=order_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.document, ModeratorFSM.check)
async def order_block(message: Message, state: FSMContext):
    text = "Данные обновлены"
    kb = inline.home_kb()
    state_data = await state.get_data()
    order_id = state_data["order_id"]
    await state.set_state(ModeratorFSM.home)
    await OrdersDAO.update(order_id=order_id, document_id=message.document.file_id)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "refuse_workers")
async def order_block(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    refusers = order["refuse_comments"]
    text = ["Отказы с комментариями:", "-" * 15]
    for refuse in refusers:
        text.append(f"{refuse['worker_username']}\n{refuse['text']}\n")
    kb = inline.home_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "all_orders")
async def order_block(callback: CallbackQuery):
    orders = await OrdersDAO.get_last()
    text = "Последние 10 ордеров:"
    kb = inline.orders_list_kb(orders=orders, excel=True)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "get_excel_orders")
async def order_block(callback: CallbackQuery):
    orders = await OrdersDAO.get_many()
    await create_excel(orders=orders)
    file = FSInputFile(path=f'{os.getcwd()}/all_orders.xlsx', filename=f"{os.getcwd()}/all_orders.xlsx")
    kb = inline.home_kb()
    await callback.message.answer_document(document=file, reply_markup=kb)
    os.remove(f'{os.getcwd()}/all_orders.xlsx')
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "find_order")
async def order_block(callback: CallbackQuery, state: FSMContext):
    text = "Введите ID ордера"
    kb = inline.home_kb()
    await state.set_state(ModeratorFSM.find_order)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, ModeratorFSM.find_order)
async def order_block(message: Message, state: FSMContext):
    order_id = message.text
    if order_id.isdigit():
        order = await OrdersDAO.get_one_or_none(id=int(order_id))
        if order:
            await full_order_profile(order=order, user_id=moderator)
            await state.set_state(ModeratorFSM.home)
            return
        else:
            text = "Ордер с таким ID не найден 🤷"
    else:
        text = "Вы ввели не число"
    kb = inline.home_kb()
    await message.answer(text, reply_markup=kb)


