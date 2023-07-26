from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.workers import Workers


class WorkerInlineKeyboard:

    def __init__(self):
        pass

    def home_kb(self):
        keyboard = [self._home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def _home_button():
        return [InlineKeyboardButton(text="🏡 Главное меню", callback_data="home")]

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="🛠 Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="📈 Статистика", callback_data="statistic")],
            [InlineKeyboardButton(text="❓ Поддержка", callback_data="support")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class WorkerSettingsInlineKeyboard(WorkerInlineKeyboard):

    def settings_kb(self, worker: dict):
        emodji = {
            "off": ("🟥", "on"),
            "on": ("🟩", "off"),
        }
        general_tuple = emodji[worker['general_status']]
        kb_row = []
        for bank in ["SBERBANK", "TINKOFF"]:
            bank_status = Workers.check_bank(workers=[worker], bank=bank)
            if worker["user_id"] in bank_status:
                button = InlineKeyboardButton(text=f"🟩 {bank}", callback_data=f"switch_bank:{bank}:off")
            else:
                button = InlineKeyboardButton(text=f"🟥 {bank}", callback_data=f"switch_bank:{bank}:on")
            kb_row.append(button)
        keyboard = [
            [InlineKeyboardButton(text=f"{general_tuple[0]}Рабочий статус",
                                  callback_data=f"general_status:{general_tuple[1]}")],
            kb_row,
            self._home_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class WorkerOrderInlineKeyboard(WorkerInlineKeyboard):

    @staticmethod
    def get_order_kb(order_id: int):
        keyboard = [
            [
                InlineKeyboardButton(text="🟩 Принять", callback_data=f"worker_order:accept:{order_id}"),
                InlineKeyboardButton(text="🟥 Отклонить", callback_data=f"worker_order:refuse:{order_id}"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def refuse_order_kb(order_id: int):
        keyboard = [[InlineKeyboardButton(text="🙅‍♂️ Отказаться", callback_data=f"worker_order:refuse:{order_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def moderation_order_kb(order_id: int):
        keyboard = [
            [
                InlineKeyboardButton(text="🟩 Принять", callback_data=f"moderation_order:accept:{order_id}"),
                InlineKeyboardButton(text="🟥 Отклонить", callback_data=f"moderation_order:refuse:{order_id}"),
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
