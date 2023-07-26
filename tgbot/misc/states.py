from aiogram.fsm.state import State, StatesGroup


class BaseFSM(StatesGroup):
    home = State()


class AdminFSM(BaseFSM):
    title_account = State()
    uid_account = State()
    private_key_account = State()


class ClientFSM(BaseFSM):
    coin_value = State()
    bank_account = State()
    comment = State()
    support = State()


class WorkerFSM(BaseFSM):
    check = State()
    refuse_comment = State()
    support = State()


class ModeratorFSM(BaseFSM):
    refuse_comment = State()
    check = State()
    find_order = State()
    support = State()
