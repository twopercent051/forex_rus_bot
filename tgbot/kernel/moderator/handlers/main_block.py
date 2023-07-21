from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from tgbot.kernel.moderator.filters import ModeratorFilter

router = Router()
router.message.filter(ModeratorFilter())
router.callback_query.filter(ModeratorFilter())


@router.message(Command('start'))
async def user_start(message: Message):
    await message.answer("Du bist ein moderator")


