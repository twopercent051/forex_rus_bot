from aiogram.types import CallbackQuery
from aiogram import F, Router

from create_bot import bot
from tgbot.kernel.worker.filters import WorkerFilter
from tgbot.kernel.worker.inline import SettingsInlineKeyboard
from tgbot.models.sql_connector import WorkersDAO
from tgbot.misc.workers import Workers

router = Router()
router.message.filter(WorkerFilter())
router.callback_query.filter(WorkerFilter())

inline = SettingsInlineKeyboard()


@router.callback_query(F.data == "settings")
async def settings_block(callback: CallbackQuery):
    worker = await WorkersDAO.get_one_or_none(user_id=str(callback.from_user.id))
    text = "НАСТРОЙКИ"
    kb = inline.settings_kb(worker=worker)
    await callback.message.answer(text=text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "general_status")
async def settings_block(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    new_status = callback.data.split(":")[1]
    bank_status = {"SBERBANK": "off", "TINKOFF": "off"}
    await WorkersDAO.update(user_id=user_id, general_status=new_status, bank_status=bank_status)
    worker = await WorkersDAO.get_one_or_none(user_id=user_id)
    kb = inline.settings_kb(worker=worker)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "switch_bank")
async def settings_block(callback: CallbackQuery):
    worker = await WorkersDAO.get_one_or_none(user_id=str(callback.from_user.id))
    if worker["general_status"] == "off":
        await bot.answer_callback_query(callback.id)
        return
    bank = callback.data.split(":")[1]
    new_status = callback.data.split(":")[2]
    worker = await Workers.switch_bank(worker=worker, bank=bank, status=new_status)
    kb = inline.settings_kb(worker=worker)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await bot.answer_callback_query(callback.id)
