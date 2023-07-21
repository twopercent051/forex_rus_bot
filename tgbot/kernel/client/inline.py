from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboard:

    @classmethod
    def home_kb(cls):
        keyboard = [cls.home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def home_button():
        return [InlineKeyboardButton(text="🏡 На главную", callback_data="home")]

    @classmethod
    def become_worker_kb(cls, user_id: str | int, username: str):
        keyboard = [
            [
                InlineKeyboardButton(text="🟩 Принять", callback_data=f"new_worker:{username}:{user_id}"),
                InlineKeyboardButton(text="🟥 Отказать", callback_data=f"new_worker:refuse:{user_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def main_menu_kb(cls):
        keyboard = [
            [InlineKeyboardButton(text="➕ Новая заявка", callback_data="transaction:new")],
            [InlineKeyboardButton(text="📄 История транзакций", callback_data="transaction:history")],
            [InlineKeyboardButton(text="❓ Поддержка", callback_data="support")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class TransactionInlineKeyboard(InlineKeyboard):

    @classmethod
    def banks_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="🟩 СберБанк", callback_data="bank:sber"),
                InlineKeyboardButton(text="🟨 Тинькофф", callback_data="bank:tinkoff"),
            ],
            [cls.home_button()]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

