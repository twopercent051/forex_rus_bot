from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config


class ModeratorFilter(BaseFilter):
    is_moderator: bool = True

    async def __call__(self, obj: Union[Message, CallbackQuery], config: Config) -> bool:
        if isinstance(obj, Message):
            var = str(obj.chat.id)
        else:
            var = str(obj.message.chat.id)
        return (var in config.tg_bot.moderator_group) == self.is_moderator
