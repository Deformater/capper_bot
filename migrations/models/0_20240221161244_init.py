from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "games" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "first_team_name" TEXT NOT NULL,
    "second_team_name" TEXT NOT NULL,
    "first_team_coefficient" DOUBLE PRECISION NOT NULL,
    "second_team_coefficient" DOUBLE PRECISION NOT NULL,
    "game_starts_at" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "tg_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "score" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "balance" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "bet_count" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "bets" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "bet_result" BOOL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "game_id" UUID NOT NULL REFERENCES "games" ("uuid") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("tg_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
