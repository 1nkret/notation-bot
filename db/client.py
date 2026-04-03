from motor.motor_asyncio import AsyncIOMotorClient

from core.env_data import mongo_url


class Database:
    client: AsyncIOMotorClient | None = None
    db = None

    @classmethod
    async def init(cls):
        cls.client = AsyncIOMotorClient(mongo_url)
        cls.db = cls.client["notatum"]

    @classmethod
    def get_db(cls):
        return cls.db
