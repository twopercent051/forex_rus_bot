from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot
from tgbot.kernel.worker.filters import WorkerFilter
from tgbot.kernel.worker.inline import InlineKeyboard
from tgbot.misc.states import WorkerFSM
from tgbot.services.garantex import GarantexAPI

router = Router()
router.message.filter(WorkerFilter())
router.callback_query.filter(WorkerFilter())

inline = InlineKeyboard()


async def main_menu(user_id: int | str, state: FSMContext):
    text = "ГЛАВНОЕ МЕНЮ"
    kb = inline.main_menu_kb()
    await state.set_state(WorkerFSM.home)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


@router.message(Command('start'))
async def main_block(message: Message, state: FSMContext):
    await main_menu(user_id=message.from_user.id, state=state)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await main_menu(user_id=callback.from_user.id, state=state)
    await bot.answer_callback_query(callback.id)
