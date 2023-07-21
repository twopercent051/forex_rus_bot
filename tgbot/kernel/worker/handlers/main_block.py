from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext

from tgbot.kernel.worker.filters import WorkerFilter

router = Router()
router.message.filter(WorkerFilter())
router.callback_query.filter(WorkerFilter())


@router.message(Command('start'))
async def user_start(message: Message):
    await message.answer('Доступ в бота возможен только из админской группы')

