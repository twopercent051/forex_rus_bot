from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from create_bot import config, bot
from tgbot.kernel.client.inline import ClientInlineKeyboard
from tgbot.kernel.client.render import main_menu_render
from tgbot.misc.states import ClientFSM
from tgbot.misc.workers import Workers
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import ClientsDAO

router = Router()

inline = ClientInlineKeyboard()

admin_ids = config.tg_bot.admin_ids


@router.message(Command("become_worker"))
async def become_worker(message: Message):
    if message.from_user.username:
        workers = await RedisConnector.get_role_redis()
        if str(message.from_user.id) in workers:
            text = "Вы уже являетесь работником 🤷"
            await Workers.create_worker(worker_id=message.from_user.id, worker_username=message.from_user.username)
        else:
            admin_text = f"⚠️ Пользователь @{message.from_user.username} подал заявку, чтобы стать работником"
            kb = inline.become_worker_kb(user_id=message.from_user.id, username=message.from_user.username)
            text = "Запрос отправлен. Ожидайте решения администратора"
            for admin in admin_ids:
                await bot.send_message(chat_id=admin, text=admin_text, reply_markup=kb)
    else:
        text = "Вам нужно создать username в Телеграм чтобы стать работником. После этого повторите запрос"
    await message.delete()
    await message.answer(text=text)


@router.message(Command("start"))
async def main_menu(message: Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else "---"
    try:
        await ClientsDAO.create(user_id=str(message.from_user.id), username=username)
    except IntegrityError:
        pass
    await state.set_state(ClientFSM.home)
    await main_menu_render(user_id=message.from_user.id, start=True)


@router.callback_query(F.data == "home")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    await main_menu_render(user_id=callback.from_user.id, start=False)
    await state.set_state(ClientFSM.home)




