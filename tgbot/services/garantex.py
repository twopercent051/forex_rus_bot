import base64
import time
import datetime
import random
import requests
import jwt
from cryptography.fernet import Fernet

from create_bot import config
from tgbot.models.sql_connector import CryptoAccountsDAO


class GarantexAPI:

    @classmethod
    def encrypt(cls, data: str) -> str:
        """Шифрование"""
        secret_key = config.misc.secret_key
        cipher_suite = Fernet(secret_key)
        return cipher_suite.encrypt(str.encode(data)).decode("utf-8")

    @classmethod
    def decrypt(cls, data: str) -> str:
        """Дешифрование"""
        secret_key = config.misc.secret_key
        cipher_suite = Fernet(secret_key)
        return cipher_suite.decrypt(str.encode(data)).decode("utf-8")

    @classmethod
    def update_jwt(cls, uid: str, private_key: str):
        try:
            key = base64.b64decode(private_key)
        except ValueError:
            return None
        iat = int(time.mktime(datetime.datetime.now().timetuple()))
        claims = {
            "exp": iat + 1.5 * 60 * 60,  # expire duration 1.5 hours
            "jti": hex(random.getrandbits(12)).upper()
        }
        jwt_token = jwt.encode(claims, key, algorithm="RS256")
        ret = requests.post('https://dauth.garantex.io/api/v1/sessions/generate_jwt',
                            json={'kid': uid, 'jwt_token': jwt_token})
        if ret.status_code != 200:
            return None
        return ret.json().get('token')

    @classmethod
    async def get_jwt(cls, account_id: int):
        account = await CryptoAccountsDAO.get_one_or_none(id=account_id)
        return cls.decrypt(account["jwt"])

    @classmethod
    async def get_wallet(cls, account_id: int):
        token = await cls.get_jwt(account_id=account_id)
        ret = requests.get('https://garantex.io/api/v2/deposit_address',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'currency': "usdt"})
        return ret.json()

    @staticmethod
    async def get_currency():
        ret = requests.get('https://garantex.io/api/v2/trades',
                           data={'market': "usdtrub", "limit": 20})
        average = 0
        for item in ret.json():
            average += float(item["price"])
        return int((average * 100) / 20)

    # @classmethod
    # async def get_client_currency(cls):
    #     market_currency = await cls.get_currency()
    #     return market_currency * (1 - config.params.client_commission)

    @classmethod
    async def get_deposit_history(cls, account_id: int, start_time: datetime, coin_value: float) -> bool:
        token = await cls.get_jwt(account_id=account_id)
        ret = requests.get('https://garantex.io/api/v2/deposits',
                           headers={'Authorization': f'Bearer {token}'},
                           data={'currency': "usdt", "start_time": start_time, "status": "accepted"})
        result = ret.json()
        for item in result:
            if float(item["amount"]) * (1 - 0.007) <= coin_value <= float(item["amount"]):
                return True
        return False

