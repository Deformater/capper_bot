from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" RENAME COLUMN "game_starts_at" TO "starts_at";
        ALTER TABLE "games" ALTER COLUMN "hype" SET NOT NULL;
        ALTER TABLE "users" ADD "success_bet_count" INT NOT NULL  DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" RENAME COLUMN "starts_at" TO "game_starts_at";
        ALTER TABLE "games" ALTER COLUMN "hype" DROP NOT NULL;
        ALTER TABLE "users" DROP COLUMN "success_bet_count";"""
