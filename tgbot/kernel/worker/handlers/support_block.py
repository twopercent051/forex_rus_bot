from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, types

from create_bot import bot, config
from tgbot.kernel.worker.filters import WorkerFilter
from tgbot.kernel.worker.inline import WorkerInlineKeyboard
from tgbot.misc.states import WorkerFSM
from tgbot.misc.support_render import support_render

router = Router()
router.message.filter(WorkerFilter())
router.callback_query.filter(WorkerFilter())

inline = WorkerInlineKeyboard()

moderator = config.tg_bot.moderator_group


@router.callback_query(F.data.split(":")[0] == "answer")
@router.callback_query(F.data == "support")
async def support_block(callback: CallbackQuery, state: FSMContext):
    text = "Напишите ваш вопрос или обращение. Вы можете приложить к сообщению фото, видео или документ"
    kb = inline.home_kb()
    await state.set_state(WorkerFSM.support)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(WorkerFSM.support)
async def support_block(message: types, state: FSMContext, album: List[Message] = None):
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    text = f"Сообщение от воркера {username}"
    await state.set_state(WorkerFSM.home)
    await support_render(album=album, message=message, target_id=moderator, title=text, sender_id=message.from_user.id)
