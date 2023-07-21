
from sqlalchemy import MetaData, inspect, Column, String, insert, select, Integer, DateTime, delete, DECIMAL, JSON, \
    TEXT, update, TIMESTAMP, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker, as_declarative
from sqlalchemy.sql import expression

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class UtcNow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(UtcNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class ClientsDB(Base):
    """Клиенты"""
    __tablename__ = "clients"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)


class WorkersDB(Base):
    """Работники"""
    __tablename__ = "workers"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    wallet = Column(String, nullable=True)
    general_status = Column(String, nullable=False, default="off")  # off on deleted
    sber_status = Column(String, nullable=False, default="off")  # off on
    tinkoff_status = Column(String, nullable=False, default="off")  # off on


class TransactionsDB(Base):
    """Заявки на перевод"""
    __tablename__ = "transactions"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    dtime = Column(TIMESTAMP, nullable=False, server_default=UtcNow())
    client_id = Column(String, nullable=False)
    client_username = Column(String, nullable=False)
    coin = Column(String, nullable=False, default="USDT")  # USDT
    coin_value = Column(DECIMAL, nullable=False)
    course = Column(DECIMAL, nullable=False)
    bank_name = Column(String, nullable=False)
    bank_account = Column(String, nullable=False)
    fiat_value = Column(DECIMAL, nullable=False)
    status = Column(String, nullable=False, default="created")  # created paid_client paid_worker accepted refused finished
    worker_id = Column(String, nullable=False)
    moderator_id = Column(String, nullable=True)
    crypto_account = Column(JSON, nullable=False)  # title + id


class CryptoAccountsDB(Base):
    """Рабочие аккаунты на бирже"""
    __tablename__ = "crypto_accounts"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    title = Column(String, nullable=False)
    jwt = Column(String, nullable=False)
    private_key = Column(TEXT, nullable=False)
    uid = Column(String, nullable=False)
    status = Column(String, nullable=False, default="off")  # off on
    processes = Column(Integer, nullable=False, default=0)


class TicketsDB(Base):
    """Обращения"""
    __tablename__ = "tickets"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    dtime = Column(TIMESTAMP, nullable=False, server_default=UtcNow())
    user_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    moderator_id = Column(String, nullable=False)
    moderator_name = Column(String, nullable=False)
    text = Column(TEXT, nullable=False)
    status = Column(String, nullable=False)  # created finished


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = None

    @classmethod
    async def get_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by).limit(1)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_many(cls, **filter_by) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data)
            result = await session.execute(stmt)
            await session.commit()
            return result.mappings().one_or_none()

    @classmethod
    async def delete(cls, **data):
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter_by(**data)
            await session.execute(stmt)
            await session.commit()


class ClientsDAO(BaseDAO):
    model = ClientsDB


class WorkersDAO(BaseDAO):
    model = WorkersDB

    @classmethod
    async def update(cls, user_id: str, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(user_id=user_id)
            await session.execute(stmt)
            await session.commit()


class TransactionsDAO(BaseDAO):
    model = TransactionsDB


class CryptoAccountsDAO(BaseDAO):
    model = CryptoAccountsDB

    @classmethod
    async def update(cls, account_id: int, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(id=account_id)
            await session.execute(stmt)
            await session.commit()


class TicketsDAO(BaseDAO):
    model = TicketsDB
