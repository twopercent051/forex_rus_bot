from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.kernel.client.inline import ClientOrderInlineKeyboard
from tgbot.misc.states import ClientFSM
from tgbot.misc.support_render import support_render

router = Router()

inline = ClientOrderInlineKeyboard()

moderator = config.tg_bot.moderator_group


@router.callback_query(F.data.split(":")[0] == "answer")
@router.callback_query(F.data == "support")
async def support_block(callback: CallbackQuery, state: FSMContext):
    text = "Напишите ваш вопрос или обращение. Вы можете приложить к сообщению фото, видео или документ"
    kb = inline.home_kb()
    await state.set_state(ClientFSM.support)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(ClientFSM.support)
async def support_block(message: types, state: FSMContext, album: List[Message] = None):
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    text = f"Сообщение от клиента {username}"
    await state.set_state(ClientFSM.home)
    await support_render(album=album, message=message, target_id=moderator, title=text, sender_id=message.from_user.id)

