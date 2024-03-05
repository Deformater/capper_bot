from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ALTER COLUMN "bet_type" TYPE VARCHAR(4) USING "bet_type"::VARCHAR(4);
        ALTER TABLE "games" ADD "second_team_fora_minus_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "first_team_fora_plus_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "first_team_total_less_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "second_team_total_bigger_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "second_team_fora_plus_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "second_team_total_less_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "first_team_fora_minus_coefficient" DOUBLE PRECISION;
        ALTER TABLE "games" ADD "first_team_total_bigger_coefficient" DOUBLE PRECISION;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "bets" ALTER COLUMN "bet_type" TYPE VARCHAR(4) USING "bet_type"::VARCHAR(4);
        ALTER TABLE "games" DROP COLUMN "second_team_fora_minus_coefficient";
        ALTER TABLE "games" DROP COLUMN "first_team_fora_plus_coefficient";
        ALTER TABLE "games" DROP COLUMN "first_team_total_less_coefficient";
        ALTER TABLE "games" DROP COLUMN "second_team_total_bigger_coefficient";
        ALTER TABLE "games" DROP COLUMN "second_team_fora_plus_coefficient";
        ALTER TABLE "games" DROP COLUMN "second_team_total_less_coefficient";
        ALTER TABLE "games" DROP COLUMN "first_team_fora_minus_coefficient";
        ALTER TABLE "games" DROP COLUMN "first_team_total_bigger_coefficient";"""
