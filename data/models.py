from tortoise import fields
from tortoise import models
from enum import Enum


class User(models.Model):
    tg_id = fields.BigIntField(unique=True, pk=True)
    username = fields.CharField(80, null=False)
    is_admin = fields.BooleanField(default=False)
    _balance = fields.FloatField(default=5000)
    bet_count = fields.IntField(default=0)
    success_bet_count = fields.IntField(default=0)
    is_subscripe = fields.BooleanField(default=False)
    bets = fields.ReverseRelation["Bet"]

    @property
    def balance(self):
        return round(self._balance, 2)

    @balance.setter
    def balance(self, value):
        self._balance = round(value, 2)

    @property
    async def success_bet_persent(self) -> float:
        if self.bet_count == 0:
            return 0

        return round((self.success_bet_count / self.bet_count) * 100, 2)

    @property
    async def place(self) -> int:
        users = await User.all().order_by("-_balance")
        return users.index(self) + 1

    class Meta:
        table = "users"


class BetType(Enum):
    WIN = "WIN"
    DRAW = "DRAW"
    DOEBLE_CHANCE = "D_CH"
    FORA_PLUS = "F_P"
    FORA_MINUS = "F_M"
    TOTAL_BIGGER = "T_B"
    TOTAL_LESS = "T_L"


class Bet(models.Model):
    uuid = fields.UUIDField(unique=True, pk=True)
    result = fields.BooleanField(null=True)
    size = fields.FloatField(null=False)
    team_name = fields.CharField(80, null=True)
    bet_type = fields.CharEnumField(BetType, null=False)
    bet_coefficient = fields.FloatField(null=False)
    balance_change = fields.FloatField(null=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="bets", to_field="tg_id", on_delete=fields.CASCADE
    )
    game: fields.ForeignKeyRelation["Game"] = fields.ForeignKeyField(
        "models.Game", related_name="bets", to_field="uuid", on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now=True)

    async def set_result(self, result: bool) -> None:
        if not (self.result is None):
            self.user.balance -= self.balance_change
            if self.result:
                self.user.success_bet_count -= 1
        if result:
            self.result = True
            self.balance_change = round(self.size * self.bet_coefficient - self.size, 2)
            self.user.success_bet_count += 1
            self.user.balance += self.balance_change + self.size
        else:
            self.result = False
            self.balance_change = -self.size

        await self.save()
        await self.user.save()

    class Meta:
        table = "bets"


class Game(models.Model):
    uuid = fields.UUIDField(unique=True, pk=True)
    first_team_name = fields.TextField(null=False)
    second_team_name = fields.TextField(null=False)
    first_team_coefficient = fields.FloatField(null=False)
    first_team_fora_plus_coefficient = fields.FloatField(null=True)
    second_team_fora_plus_coefficient = fields.FloatField(null=True)
    first_team_fora_minus_coefficient = fields.FloatField(null=True)
    second_team_fora_minus_coefficient = fields.FloatField(null=True)
    total_bigger_coefficient = fields.FloatField(null=True)
    total_less_coefficient = fields.FloatField(null=True)
    first_team_double_chance = fields.FloatField(null=True)
    second_team_coefficient = fields.FloatField(null=False)
    second_team_double_chance = fields.FloatField(null=True)
    draw_coefficient = fields.FloatField(null=True)
    first_team_score = fields.IntField(null=True)
    second_team_score = fields.IntField(null=True)
    format = fields.CharField(max_length=10, null=False)
    starts_at = fields.DatetimeField(null=False)
    hype = fields.IntField(null=False)
    bets = fields.ReverseRelation["Bet"]

    async def set_winner(self, name: str) -> None:
        for bet in self.bets:
            await bet.set_result(bet.team_name == name)
        self.winner = name
        await self.save()

    async def set_score(self, score: list[float]) -> None:
        self.first_team_score = score[0]
        self.second_team_score = score[1]
        for bet in self.bets:
            match bet.bet_type:
                case BetType.WIN:
                    if bet.team_name == self.first_team_name:
                        await bet.set_result(score[0] > score[1])
                    else:
                        await bet.set_result(score[0] < score[1])
                case BetType.DRAW:
                    await bet.set_result(score[0] == score[1])
                case BetType.DOEBLE_CHANCE:
                    if bet.team_name == self.first_team_name:
                        await bet.set_result(score[0] > 0)
                    else:
                        await bet.set_result(score[1] > 0)
                case BetType.FORA_PLUS:
                    if bet.team_name == self.first_team_name:
                        await bet.set_result(score[0] - score[1] > 1.5)
                    else:
                        await bet.set_result(score[1] - score[0] > 1.5)
                case BetType.FORA_MINUS:
                    if bet.team_name == self.first_team_name:
                        await bet.set_result(score[0] - score[1] < 1.5)
                    else:
                        await bet.set_result(score[1] - score[0] < 1.5)
                case BetType.TOTAL_BIGGER:
                    await bet.set_result(score[0] + score[1] > 2.5)
                case BetType.TOTAL_LESS:
                    await bet.set_result(score[0] + score[1] < 2.5)

        await self.save()

    class Meta:
        table = "games"
