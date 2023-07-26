from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ClientInlineKeyboard:

    def __init__(self):
        pass

    def home_kb(self):
        keyboard = [self.home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def home_button():
        return [InlineKeyboardButton(text="🏡 Главное меню", callback_data="home")]

    @staticmethod
    def become_worker_kb(user_id: str | int, username: str):
        keyboard = [
            [
                InlineKeyboardButton(text="🟩 Принять", callback_data=f"new_worker:{username}:{user_id}"),
                InlineKeyboardButton(text="🟥 Отказать", callback_data=f"new_worker:refuse:{user_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="➕ Новый ордер", callback_data="order:new")],
            [InlineKeyboardButton(text="📄 История ордеров", callback_data="order:history")],
            [InlineKeyboardButton(text="❓ Поддержка", callback_data="support")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class ClientOrderInlineKeyboard(ClientInlineKeyboard):

    def banks_kb(self):
        keyboard = [
            [
                InlineKeyboardButton(text="🟩 SBERBANK", callback_data="bank:SBERBANK"),
                InlineKeyboardButton(text="🟨 TINKOFF", callback_data="bank:TINKOFF"),
            ],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def pass_comment_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="↪️ Пропустить", callback_data="pass_comment")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def accept_order_kb(self, task_id: str):
        keyboard = [
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"accept_order:{task_id}")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def order_paid_kb(order_id: int, task_id: str):
        keyboard = [
            [InlineKeyboardButton(text="👍 Перевод отправлен", callback_data=f"paid:{order_id}:{task_id}")],
            [InlineKeyboardButton(text="❌ Отменить ордер", callback_data=f"ct:{order_id}:{task_id}")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def orders_history_kb(self, orders: list):
        keyboard = []
        for order in orders:
            keyboard.append([InlineKeyboardButton(text=f"Ордер № {order['id']}",
                                                  callback_data=f"order_profile:{order['id']}")])
        keyboard.append(self.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def support_order_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="❓ Поддержка", callback_data="support")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


