from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from create_bot import config, bot
from tgbot.kernel.client.inline import TransactionInlineKeyboard
from tgbot.misc.states import ClientFSM
from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import ClientsDAO, CryptoAccountsDAO, WorkersDAO
from tgbot.services.garantex import GarantexAPI

router = Router()



@router.callback_query(F.data.split(":")[0] == "transaction")
async def transaction_block(callback: CallbackQuery):
    transaction = callback.data.split(":")[1]
    if transaction == "new":
        free_accounts = await CryptoAccountsDAO.get_many(status="on")
        if len(free_accounts) == 0:
            text = "К сожалению, сейчас у нас нет возможности сделать перевод, попробуйте позднее или напишите нам в " \
                   "поддержку"
            kb = TransactionInlineKeyboard.home_kb()
        else:
            text = "Выберите банк, на который желаете получить перевод"
            kb = TransactionInlineKeyboard.banks_kb()
    else:
        pass
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "bank")
async def transaction_block(callback: CallbackQuery, state: FSMContext):
    bank = callback.data.split(":")[1]
    currency = await GarantexAPI.get_currency()
    if bank == "sber":
        free_workers = await WorkersDAO.get_many(sber_status="on")
    else:
        free_workers = await WorkersDAO.get_many(tinkoff_status="on")
    if len(free_workers) == 0:
        text = "В настоящий момент нет предложения на обмен в этот банк. Выберите другой банк или попробуйте позднее"
    else:
        text = f"В настоящий момент обменный курс составляет " \
               f"<i>{currency * (1 - config.params.client_commission)}</i>. Введите объём в USDT, который хотите " \
               f"обменять"
        await state.update_data(bank_name=bank)
        await state.set_state(ClientFSM.coin_value)
    kb = TransactionInlineKeyboard.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)

