from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ADD "command_name" VARCHAR(80) NOT NULL;
        ALTER TABLE "bets" RENAME COLUMN "bet_result" TO "result";
        ALTER TABLE "bets" ADD "size" DOUBLE PRECISION NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" RENAME COLUMN "result" TO "bet_result";
        ALTER TABLE "bets" DROP COLUMN "command_name";
        ALTER TABLE "bets" DROP COLUMN "size";"""
