import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from redis.asyncio import Redis

from router import dlg_router, interesting_games
from routers.game_add import game_add_router

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
    dp.include_router(game_add_router)
    bot = Bot(settings.TOKEN)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(interesting_games, "cron", hour=8, minute=30, args=(bot,))
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
