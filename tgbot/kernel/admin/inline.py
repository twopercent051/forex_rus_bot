from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class InlineKeyboard:
    @classmethod
    def main_menu_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="Аккаунты Garantex", callback_data="accounts"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def home_kb(cls):
        keyboard = [cls.home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def home_button():
        return [InlineKeyboardButton(text="🏡 На главную", callback_data="home")]


class AccountsInlineKeyboard(InlineKeyboard):

    @classmethod
    def accounts_list_kb(cls, accounts: list):
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
        keyboard.append(cls.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
