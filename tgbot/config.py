from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class RedisConfig:
    host: str
    port: str
    db: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool
    moderator_group: str


@dataclass
class Miscellaneous:
    secret_key: str


@dataclass
class Parameters:
    client_commission: float
    worker_commission: float
    deposit_commission: float


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    rds: RedisConfig
    misc: Miscellaneous
    params: Parameters


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            moderator_group=env.str('MODERATOR_GROUP')
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        rds=RedisConfig(
            host=env.str('REDIS_HOST'),
            port=env.str('REDIS_PORT'),
            db=env.str('REDIS_DB')
        ),
        misc=Miscellaneous(
            secret_key=env.str("SECRET_KEY")
        ),
        params=Parameters(
            client_commission=0.05,
            worker_commission=0.02,
            deposit_commission=0.0025
        )
    )
