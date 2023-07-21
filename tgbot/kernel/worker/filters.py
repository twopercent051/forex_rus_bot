from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from tgbot.config import Config
from tgbot.models.redis_connector import RedisConnector as rds


class WorkerFilter(BaseFilter):
    is_worker: bool = True

    async def __call__(self, obj: Union[Message, CallbackQuery], config: Config) -> bool:
        if isinstance(obj, Message):
            var = obj.chat.id
        else:
            var = obj.message.chat.id
        if var in config.tg_bot.admin_ids:
            return True
        workers = await rds.get_role_redis("worker")
        return (str(var) in workers) == self.is_worker
