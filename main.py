import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from redis.asyncio import Redis

from router import dlg_router

from data.init import register_db, upgrade_db

import settings


async def init_db(config):
    await register_db(config)
    await upgrade_db(config)


async def main() -> None:
    await init_db(config=settings.TORTOISE_ORM)

    storage = RedisStorage(
        redis=Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            password=settings.REDIS_PASSWORD,
        ),
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )

    dp = Dispatcher(storage=storage)
    dp.include_router(dlg_router)
    bot = Bot(settings.TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
