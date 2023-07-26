from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router

from create_bot import bot, config
from tgbot.kernel.admin.filters import AdminFilter
from tgbot.kernel.admin.inline import AdminAccountsInlineKeyboard
from tgbot.misc.states import AdminFSM
from tgbot.models.sql_connector import CryptoAccountsDAO
from tgbot.services.garantex import GarantexAPI

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = AdminAccountsInlineKeyboard()

admin_ids = config.tg_bot.admin_ids


@router.callback_query(F.data == "accounts")
async def accounts(callback: CallbackQuery):
    text = "Список действующих аккаунтов"
    accounts_list = await CryptoAccountsDAO.get_many()
    kb = inline.accounts_list_kb(accounts=accounts_list)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "account")
async def accounts(callback: CallbackQuery, state: FSMContext):
    clb_data = callback.data.split(":")[1]
    if clb_data == "create":
        text = "Введите название аккаунта для удобной ориентации в системе"
        kb = inline.home_kb()
        await state.set_state(AdminFSM.title_account)
        await callback.message.answer(text, reply_markup=kb)
    elif clb_data == "delete":
        account_id = int(callback.data.split(":")[2])
        await CryptoAccountsDAO.delete(id=account_id)
        accounts_list = await CryptoAccountsDAO.get_many()
        kb = inline.accounts_list_kb(accounts=accounts_list)
        await callback.message.edit_reply_markup(reply_markup=kb)
    else:
        account_id = int(callback.data.split(":")[2])
        await CryptoAccountsDAO.update(account_id=account_id, status=clb_data)
        accounts_list = await CryptoAccountsDAO.get_many()
        kb = inline.accounts_list_kb(accounts=accounts_list)
        await callback.message.edit_reply_markup(reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.title_account)
async def accounts(message: Message, state: FSMContext):
    account_title = message.text.strip()
    account = await CryptoAccountsDAO.get_one_or_none(title=account_title)
    if account:
        text = "Аккаунт с таким именем уже существует. Введите другое"
    else:
        text = "Введите UID аккаунта"
        await state.update_data(account_title=message.text.strip())
        await state.set_state(AdminFSM.uid_account)
    kb = inline.home_kb()
    await message.delete()
    await message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.uid_account)
async def accounts(message: Message, state: FSMContext):
    text = "Введите PRIVATE KEY аккаунта"
    kb = inline.home_kb()
    await state.update_data(account_uid=message.text)
    await state.set_state(AdminFSM.private_key_account)
    await message.delete()
    await message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.private_key_account)
async def accounts(message: Message, state: FSMContext):
    text = "⏳ Проверяем..."
    msg = await message.answer(text)
    state_data = await state.get_data()
    private_key = message.text.strip()
    jwt_token = GarantexAPI.update_jwt(uid=state_data["account_uid"], private_key=private_key)
    await msg.delete()
    if jwt_token:
        text = f"Аккаунт {state_data['account_title']} сохранён"
        encrypted_uid = GarantexAPI.encrypt(data=state_data["account_uid"])
        encrypted_private_key = GarantexAPI.encrypt(data=private_key)
        encrypted_jwt = GarantexAPI.encrypt(data=jwt_token)
        await CryptoAccountsDAO.create(title=state_data['account_title'],
                                       jwt=encrypted_jwt,
                                       private_key=encrypted_private_key,
                                       uid=encrypted_uid)
    else:
        text = "Данные введены неверно"
    kb = inline.home_kb()
    await message.delete()
    await message.answer(text, reply_markup=kb)
