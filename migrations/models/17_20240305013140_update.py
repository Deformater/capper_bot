from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" RENAME COLUMN "first_team_total_bigger_coefficient" TO "total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "second_team_total_bigger_coefficient" TO "total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "first_team_total_less_coefficient" TO "total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "second_team_total_less_coefficient" TO "total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "first_team_total_bigger_coefficient" TO "total_bigger_coefficient";
        ALTER TABLE "games" RENAME COLUMN "second_team_total_bigger_coefficient" TO "total_bigger_coefficient";
        ALTER TABLE "games" RENAME COLUMN "first_team_total_less_coefficient" TO "total_bigger_coefficient";
        ALTER TABLE "games" RENAME COLUMN "second_team_total_less_coefficient" TO "total_bigger_coefficient";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "games" RENAME COLUMN "total_bigger_coefficient" TO "second_team_total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_less_coefficient" TO "second_team_total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_bigger_coefficient" TO "first_team_total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_less_coefficient" TO "first_team_total_less_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_bigger_coefficient" TO "first_team_total_bigger_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_less_coefficient" TO "first_team_total_bigger_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_bigger_coefficient" TO "second_team_total_bigger_coefficient";
        ALTER TABLE "games" RENAME COLUMN "total_less_coefficient" TO "second_team_total_bigger_coefficient";"""
