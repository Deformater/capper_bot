from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" ADD "format" VARCHAR(10);
        ALTER TABLE "users" ADD "is_subscripe" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "users" ALTER COLUMN "balance" SET DEFAULT 5000;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" DROP COLUMN "format";
        ALTER TABLE "users" DROP COLUMN "is_subscripe";
        ALTER TABLE "users" ALTER COLUMN "balance" SET DEFAULT 0;"""
