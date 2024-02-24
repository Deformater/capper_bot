from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ADD "bet_type" VARCHAR(13) NOT NULL;
        ALTER TABLE "bets" ALTER COLUMN "team_name" DROP NOT NULL;
        ALTER TABLE "games" ADD "second_team_score" INT;
        ALTER TABLE "games" ADD "second_team_double_chance" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "first_team_score" INT;
        ALTER TABLE "games" ADD "draw_coefficient" DOUBLE PRECISION NOT NULL;
        ALTER TABLE "games" ADD "first_team_double_chance" DOUBLE PRECISION;
        ALTER TABLE "games" DROP COLUMN "winner";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" DROP COLUMN "bet_type";
        ALTER TABLE "bets" ALTER COLUMN "team_name" SET NOT NULL;
        ALTER TABLE "games" ADD "winner" TEXT;
        ALTER TABLE "games" DROP COLUMN "second_team_score";
        ALTER TABLE "games" DROP COLUMN "second_team_double_chance";
        ALTER TABLE "games" DROP COLUMN "first_team_score";
        ALTER TABLE "games" DROP COLUMN "draw_coefficient";
        ALTER TABLE "games" DROP COLUMN "first_team_double_chance";"""
