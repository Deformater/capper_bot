from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" RENAME COLUMN "command_name" TO "team_name";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" RENAME COLUMN "team_name" TO "command_name";"""
