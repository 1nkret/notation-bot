from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from core.env_data import token, redis_url


if redis_url:
    storage = RedisStorage.from_url(redis_url)
else:
    from aiogram.fsm.storage.base import BaseStorage
    storage = BaseStorage()


bot = Bot(token=token)
dp = Dispatcher(storage=storage)
