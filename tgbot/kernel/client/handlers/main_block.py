from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from create_bot import config, bot
from tgbot.kernel.client.inline import InlineKeyboard
from tgbot.misc.states import ClientFSM
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import ClientsDAO
from tgbot.services.garantex import GarantexAPI

router = Router()

admin_ids = config.tg_bot.admin_ids


@router.message(Command('test'))
async def test(message: Message):
    a = await GarantexAPI.get_currency()
    print(a)


@router.message(Command("become_worker"))
async def become_worker(message: Message):
    if message.from_user.username:
        workers = await RedisConnector.get_role_redis()
        if str(message.from_user.id) in workers:
            text = "Вы уже являетесь работником 🤷"
        else:
            admin_text = f"⚠️ Пользователь @{message.from_user.username} подал заявку, чтобы стать работником"
            kb = InlineKeyboard.become_worker_kb(user_id=message.from_user.id, username=message.from_user.username)
            text = "Запрос отправлен. Ожидайте решения администратора"
            for admin in admin_ids:
                await bot.send_message(chat_id=admin, text=admin_text, reply_markup=kb)
    else:
        text = "Вам нужно создать username в Телеграм чтобы стать работником. После этого повторите запрос"
    await message.delete()
    await message.answer(text=text)


async def main_menu_render(user_id: int | str, start: bool):
    if start:
        text = "Добро пожаловать в ForexRub. Здесь вы можете быстро обменять USDT в рубль переводом на карту " \
               "Сбербанка или Тинькофф. Просто создайте заявку. Если у вас возникнут какие-либо вопросы смело пишите " \
               "в поддержку, ответим в ближайшее время"
    else:
        text = "Главное меню"
    kb = InlineKeyboard.main_menu_kb()
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)


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




