from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.models.sql_connector import WorkersDAO


class AdminInlineKeyboard:

    def __init__(self):
        pass

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="📝 Аккаунты Garantex", callback_data="accounts")],
            [InlineKeyboardButton(text="🔧 Воркеры", callback_data="workers")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="statistic")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def home_kb(self):
        keyboard = [self.home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def home_button():
        return [InlineKeyboardButton(text="🏡 На главную", callback_data="home")]


class AdminAccountsInlineKeyboard(AdminInlineKeyboard):

    def accounts_list_kb(self, accounts: list):
        keyboard = []
        for account in accounts:
            emodji = {
                "off": ("🟥", "on"),
                "on": ("🟩", "off"),
            }
            keyboard.append(
                [
                    InlineKeyboardButton(text=f"{emodji[account['status']][0]} {account['title']}",
                                         callback_data=f"account:{emodji[account['status']][1]}:{account['id']}"),
                    InlineKeyboardButton(text="🗑 Удалить", callback_data=f"account:delete:{account['id']}"),
                ]
            )
        keyboard.append([InlineKeyboardButton(text="➕ Добавить аккаунт", callback_data=f"account:create")])
        keyboard.append(self.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class AdminWorkersInlineKeyboard(AdminInlineKeyboard):

    async def workers_list_kb(self, workers: list):
        keyboard = []
        for worker_id in workers:
            worker = await WorkersDAO.get_one_or_none(user_id=str(worker_id))
            keyboard.append(
                [
                    InlineKeyboardButton(text=worker["username"], callback_data=f"worker:{worker_id}"),
                    InlineKeyboardButton(text="🫵 Уволить", callback_data=f"worker_delete:{worker_id}"),
                ]
            )
        keyboard.append(self.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def delete_worker_kb(self, worker_id: str | int):
        keyboard = [
            [InlineKeyboardButton(text="🫵 Уволить", callback_data=f"worker_delete:{worker_id}")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
