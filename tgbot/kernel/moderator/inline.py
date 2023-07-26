from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ModeratorInlineKeyboard:

    def __init__(self):
        pass

    def home_kb(self):
        keyboard = [self.home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def home_button():
        return [InlineKeyboardButton(text="🏡 Главное меню", callback_data="home")]

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="📋 Ордера", callback_data="orders")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class ModeratorOrderInlineKeyboard(ModeratorInlineKeyboard):

    def orders_menu_kb(self):
        keyboard = [
            [InlineKeyboardButton(text="⚠️ Активные ордера", callback_data="active_orders")],
            [InlineKeyboardButton(text="📋 Все ордера", callback_data="all_orders")],
            [InlineKeyboardButton(text="🔎 Поиск по ID", callback_data="find_order")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def answer_kb(sender_id: str | int):
        keyboard = [[InlineKeyboardButton(text="↪️ Ответить", callback_data=f"answer:{sender_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def orders_list_kb(self, orders: list, excel=False):
        keyboard = []
        emodji = dict(created="🆕",
                      paid_client="⚠️",
                      paid_worker="⚠️",
                      refused="📛",
                      finished="✅",
                      cancelled="🤷")
        for order in orders:
            keyboard.append([InlineKeyboardButton(text=f"{emodji[order['status']]} Ордер № {order['id']}",
                                                  callback_data=f"order_profile:{order['id']}")])
        if excel:
            keyboard.append([InlineKeyboardButton(text="🗃 Вся выгрузка", callback_data="get_excel_orders")])
        keyboard.append(self.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def order_profile_kb(self, order: dict):
        order_id = order["id"]
        worker_id = order["worker_id"] if order["worker_id"] and order["worker_id"] != "---" else None
        keyboard = [
            [InlineKeyboardButton(text="🛠 Назначить воркера", callback_data=f"set_workers:{order_id}")],
            [InlineKeyboardButton(text="📝 Прикрепить чек", callback_data=f"set_check:{order_id}")],
        ]
        if order["status"] not in ["finished", "cancelled"] and worker_id:
            keyboard.append([InlineKeyboardButton(text="⚓️ Завершить заказ", callback_data=f"finish_order:{order_id}")])
        if len(order["refuse_comments"]) > 0:
            keyboard.append([InlineKeyboardButton(text="🙅‍♂️ Отказники", callback_data=f"refuse_workers:{order_id}")])
        keyboard.append(self.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def workers_list_kb(self, workers: list, order_id: int | str):
        keyboard = []
        for worker in workers:
            keyboard.append([InlineKeyboardButton(text=worker["username"],
                                                  callback_data=f"set_worker:{order_id}:{worker['user_id']}")])
        keyboard.append(self.home_button())
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def finish_order_kb(self, order_id: int | str):
        keyboard = [
            [InlineKeyboardButton(text="❗️ Завершить ордер", callback_data=f"finish_order_accept:{order_id}")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def set_check_kb(self, order_id: int | str):
        keyboard = [
            [InlineKeyboardButton(text="📝 Прикрепить чек", callback_data=f"set_check:{order_id}")],
            self.home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
