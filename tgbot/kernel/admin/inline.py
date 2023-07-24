from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class InlineKeyboard:

    def __init__(self):
        pass

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [
                InlineKeyboardButton(text="Аккаунты Garantex", callback_data="accounts"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def home_kb(self):
        keyboard = [self._home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def _home_button():
        return [InlineKeyboardButton(text="🏡 На главную", callback_data="home")]


class AccountsInlineKeyboard(InlineKeyboard):

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
        keyboard.append(self._home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
