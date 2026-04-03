import asyncio
import logging

from core.config import bot, dp
from db.client import Database
from db.mongo import setup_indexes
from utils.load_routers import load_routers
from bot.catch_all.handlers import router as catch_all_router


async def main():
    logging.basicConfig(level=logging.INFO)

    await Database.init()
    await setup_indexes()

    router = load_routers()
    dp.include_router(router)
    dp.include_router(catch_all_router)

    logging.info("Notatum bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
