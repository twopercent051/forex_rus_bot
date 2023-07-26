from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.kernel.moderator.filters import ModeratorFilter
from tgbot.kernel.moderator.inline import ModeratorOrderInlineKeyboard
from tgbot.misc.states import ModeratorFSM
from tgbot.misc.support_render import support_render

router = Router()
router.message.filter(ModeratorFilter())
router.callback_query.filter(ModeratorFilter())

admin_ids = config.tg_bot.admin_ids
moderator = config.tg_bot.moderator_group

inline = ModeratorOrderInlineKeyboard()


@router.callback_query(F.data.split(":")[0] == "answer")
async def support_block(callback: CallbackQuery, state: FSMContext):
    target_id = callback.data.split(":")[1]
    text = "Напишите ваш вопрос или обращение. Вы можете приложить к сообщению фото, видео или документ"
    kb = inline.home_kb()
    await state.set_state(ModeratorFSM.support)
    await state.update_data(target_id=target_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(ModeratorFSM.support)
async def support_block(message: types, state: FSMContext, album: List[Message] = None):
    text = f"Сообщение от администратора"
    state_data = await state.get_data()
    target_id = state_data["target_id"]
    await state.set_state(ModeratorFSM.home)
    await support_render(album=album, message=message, target_id=target_id, title=text, sender_id=message.from_user.id)
