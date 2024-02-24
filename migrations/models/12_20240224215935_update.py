from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ALTER COLUMN "bet_type" TYPE VARCHAR(4) USING "bet_type"::VARCHAR(4);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ALTER COLUMN "bet_type" TYPE VARCHAR(13) USING "bet_type"::VARCHAR(13);"""
