import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import F, Router

from create_bot import bot, config
from tgbot.kernel.moderator.render import order_moderator_render
from tgbot.kernel.worker.filters import WorkerFilter
from tgbot.kernel.worker.handlers.main_block import main_menu
from tgbot.kernel.worker.inline import WorkerOrderInlineKeyboard
from tgbot.kernel.worker.render import order_worker_render
from tgbot.misc.states import WorkerFSM
from tgbot.models.sql_connector import WorkersDAO, OrdersDAO

router = Router()
router.message.filter(WorkerFilter())
router.callback_query.filter(WorkerFilter())

inline = WorkerOrderInlineKeyboard()

moderator = config.tg_bot.moderator_group


@router.callback_query(F.data.split(":")[0] == "worker_order")
async def order_block(callback: CallbackQuery, state: FSMContext):
    decision = callback.data.split(":")[1]
    order_id = int(callback.data.split(":")[2])
    order = await OrdersDAO.get_one_or_none(id=order_id)
    if order["worker_id"] != str(callback.from_user.id) or order["status"] != "paid_client":
        await callback.message.answer("Ордер неактуален")
        await bot.answer_callback_query(callback.id)
        return
    if decision == "accept":
        user_id = str(callback.from_user.id)
        text = "Переведите деньги по указанным в сообщении реквизитам и отправьте чек об оплате"
        kb = inline.refuse_order_kb(order_id=order_id)
        # remind_task_id = f"rem_{user_id}_{int(time.time())}"
        # cancel_task_id = f"can_{user_id}_{int(time.time())}"
        # await CreateTask.remind_worker_order(user_id=user_id, order_id=order_id, task_id=remind_task_id)
        # await CreateTask.cancel_worker_order(user_id=user_id, order_id=order_id, task_id=cancel_task_id,
        #                                      remind_task_id=remind_task_id)
        await state.set_state(WorkerFSM.check)
        await OrdersDAO.update(order_id=order_id, worker_id=user_id)
    else:  # refuse
        text = "⚠️ Заказ снят. Напишите причину отказа."
        kb = None
        await state.set_state(WorkerFSM.refuse_comment)
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(order_id=order_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.document, WorkerFSM.check)
async def order_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    order_id = state_data["order_id"]
    doc_id = message.document.file_id
    await OrdersDAO.update(order_id=order_id,
                           worker_id=str(message.from_user.id),
                           document_id=doc_id,
                           status="paid_worker")
    order = await OrdersDAO.get_one_or_none(id=order_id)
    worker_text = "Отправили чек на модерацию. Ожидайте.. ⏳"
    await message.answer(worker_text)
    order_text = order_moderator_render(order=order, worker_username=f"@{message.from_user.username}")
    text = "☝️ Проверьте перевод"
    kb = inline.moderation_order_kb(order_id=order_id)
    await bot.send_message(chat_id=moderator, text=order_text)
    await bot.send_document(chat_id=moderator, document=doc_id)
    await bot.send_message(chat_id=moderator, text=text, reply_markup=kb)
    await asyncio.sleep(5)
    await main_menu(user_id=message.from_user.id, state=state)


@router.message(F.text, WorkerFSM.refuse_comment)
async def order_block(message: Message, state: FSMContext):
    state_data = await state.get_data()
    order_id = state_data["order_id"]
    order = await OrdersDAO.get_one_or_none(id=order_id)
    refuse_comments: list = order["refuse_comments"]
    stop_list: list = order["stop_list"]
    refuse_comments.append(dict(worker_username=f"@{message.from_user.username}", text=message.text))
    stop_list.append(str(message.from_user.id))
    await OrdersDAO.update(order_id=order_id, stop_list=stop_list, refuse_comments=refuse_comments)
    free_worker = await WorkersDAO.get_free(stop_list=stop_list)
    if len(free_worker) == 0:
        mod_text = f"⚠️ На заявку № {order_id} не удалось найти отправителя"
        await OrdersDAO.update(order_id=order_id, worker_id="---")
        await bot.send_message(chat_id=moderator, text=mod_text)
    else:
        await order_worker_render(order=order, worker_id=free_worker[0]["user_id"])
    await main_menu(user_id=message.from_user.id, state=state)


