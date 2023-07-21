import redis
import json

from create_bot import config, logger

r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)


class RedisConnector:

    @classmethod
    def redis_start(cls):
        r.set("worker", json.dumps(list()))
        # r.set("moderator", json.dumps(list()))
        logger.info('Redis connected OK')

    @classmethod
    async def create_role_redis(cls, user_id, role="worker"):
        response = r.get(role).decode('utf-8')
        user_list = json.loads(response)
        user_list.append(user_id)
        r.set(role, json.dumps(user_list))

    @classmethod
    async def get_role_redis(cls, role="worker"):
        response = r.get(role)
        if response is None:
            return []
        response = r.get(role).decode('utf-8')
        user_list = json.loads(response)
        return user_list

    @classmethod
    async def delete_role_redis(cls, user_id, role="worker"):
        response = r.get(role).decode('utf-8')
        user_list = json.loads(response)
        user_list.remove(user_id)
        r.set(role, json.dumps(user_list))
