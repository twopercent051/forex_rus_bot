from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from create_bot import bot, config
from tgbot.kernel.moderator.filters import ModeratorFilter
from tgbot.kernel.moderator.render import main_menu_render
from tgbot.misc.states import ModeratorFSM

router = Router()
router.message.filter(ModeratorFilter())
router.callback_query.filter(ModeratorFilter())

moderator = config.tg_bot.moderator_group


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await main_menu_render(moderator_id=moderator)
    await state.set_state(ModeratorFSM.home)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await main_menu_render(moderator_id=moderator)
    await state.set_state(ModeratorFSM.home)
    await bot.answer_callback_query(callback.id)


