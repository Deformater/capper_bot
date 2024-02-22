from tortoise import fields
from tortoise import models
from enum import Enum


class User(models.Model):
    tg_id = fields.BigIntField(unique=True, pk=True)
    username = fields.CharField(80, null=False)
    score = fields.FloatField(default=0)
    balance = fields.FloatField(default=5000)
    bet_count = fields.IntField(default=0)
    success_bet_count = fields.IntField(default=0)
    is_subscripe = fields.BooleanField(default=False)
    bets = fields.ReverseRelation["Bet"]

    @property
    async def success_bet_persent(self) -> float:
        if self.bet_count == 0:
            return 0

        return self.success_bet_count / self.bet_count * 100

    @property
    async def place(self) -> int:
        users = await User.all().order_by("-balance")
        return users.index(self) + 1

    class Meta:
        table = "users"


class Bet(models.Model):
    uuid = fields.UUIDField(unique=True, pk=True)
    result = fields.BooleanField(null=True)
    size = fields.FloatField(null=False)
    team_name = fields.CharField(80, null=False)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="bets", to_field="tg_id", on_delete=fields.CASCADE
    )
    game: fields.ForeignKeyRelation["Game"] = fields.ForeignKeyField(
        "models.Game", related_name="bets", to_field="uuid", on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "bets"


class Game(models.Model):
    uuid = fields.UUIDField(unique=True, pk=True)
    first_team_name = fields.TextField(null=False)
    second_team_name = fields.TextField(null=False)
    first_team_coefficient = fields.FloatField(null=False)
    second_team_coefficient = fields.FloatField(null=False)
    format = fields.CharField(max_length=10, null=False)
    starts_at = fields.DatetimeField(null=False)
    hype = fields.IntField(null=False)

    class Meta:
        table = "games"
