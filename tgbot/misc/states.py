from aiogram.fsm.state import State, StatesGroup


class BaseFSM(StatesGroup):
    home = State()


class AdminFSM(BaseFSM):
    title_account = State()
    uid_account = State()
    private_key_account = State()


class ClientFSM(BaseFSM):
    coin_value = State()
