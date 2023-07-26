from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, config
from tgbot.kernel.admin.filters import AdminFilter
from tgbot.kernel.admin.inline import AdminInlineKeyboard
from tgbot.kernel.admin.render import main_menu_render
from tgbot.misc.workers import Workers

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = AdminInlineKeyboard()


admin_ids = config.tg_bot.admin_ids


@router.callback_query(F.data.split(":")[0] == "new_worker")
async def new_worker(callback: CallbackQuery):
    user_id = callback.data.split(":")[2]
    if callback.data.split(":")[1] == "refuse":
        user_text = "Вам отказано в получении статуса 🤷. Обратитесь в поддержку для разъяснений"
        text = "Сотрудник получил отказ"
    else:
        username = callback.data.split(":")[1]
        user_text = "Вы получили статус сотрудника 🎉"
        await Workers.create_worker(worker_id=user_id, worker_username=username)
        text = f"Пользователь @{username} получил статус сотрудника"
    for admin in admin_ids:
        await bot.send_message(chat_id=admin, text=text)
    await bot.send_message(chat_id=user_id, text=user_text)


@router.message(Command("start"))
async def main_menu(message: Message, state: FSMContext):
    await main_menu_render(user_id=message.from_user.id, start=True, state=state)


@router.callback_query(F.data == "home")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await main_menu_render(user_id=callback.from_user.id, start=False, state=state)
    await bot.answer_callback_query(callback.id)

