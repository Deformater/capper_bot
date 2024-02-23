from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ADD "bet_coefficient" DOUBLE PRECISION NOT NULL;
        ALTER TABLE "bets" ADD "balance_change" DOUBLE PRECISION;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" DROP COLUMN "bet_coefficient";
        ALTER TABLE "bets" DROP COLUMN "balance_change";"""
