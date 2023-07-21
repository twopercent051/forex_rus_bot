from sqlalchemy.exc import IntegrityError

from tgbot.models.redis_connector import RedisConnector
from tgbot.models.sql_connector import WorkersDAO


class Workers:

    @classmethod
    async def create_worker(cls, worker_id: int | str, worker_username: str):
        await RedisConnector.create_role_redis(user_id=str(worker_id))
        try:
            await WorkersDAO.create(user_id=str(worker_id), username=f"@{worker_username}", wallet="")
        except IntegrityError:
            await WorkersDAO.update(user_id=str(worker_id), general_status="off")

    @classmethod
    async def delete_worker(cls, worker_id: int | str):
        await RedisConnector.delete_role_redis(user_id=str(worker_id))
        await WorkersDAO.update(user_id=str(worker_id), general_status="deleted")
