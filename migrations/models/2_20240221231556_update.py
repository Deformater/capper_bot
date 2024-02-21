from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" ADD "hype" INT;
        ALTER TABLE "games" ALTER COLUMN "format" SET NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" DROP COLUMN "hype";
        ALTER TABLE "games" ALTER COLUMN "format" DROP NOT NULL;"""
