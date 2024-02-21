from tortoise import Tortoise
from aerich import Command


async def register_db(config):
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()


async def upgrade_db(config):
    command = Command(tortoise_config=config, app="models")
    await command.init()
    await command.upgrade(run_in_transaction=False)
