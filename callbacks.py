from aiogram.filters.callback_data import CallbackData
from pydantic import UUID4


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class ContinueCallback(CallbackData, prefix="continue"):
    pass


class GameCallback(CallbackData, prefix="game"):
    game_uuid: UUID4


class BetCallback(CallbackData, prefix="bet"):
    game_uuid: UUID4
    content: int
    bet_type: str = None


class Bo2BetCallback(CallbackData, prefix="bo2_bet"):
    game_uuid: UUID4
    content: int


class Bo2TeamBetCallback(CallbackData, prefix="bo2_team"):
    game_uuid: UUID4
    bet_type: str
    bet_coefficient: float


class Bo3BetCallback(CallbackData, prefix="bo3_bet"):
    game_uuid: UUID4
    content: int


class Bo3TeamBetCallback(CallbackData, prefix="bo3_team"):
    game_uuid: UUID4
    bet_type: str
    bet_coefficient: float


class MoreBetCallback(CallbackData, prefix="more_bet"):
    bets_amount: int


class MoreTeamCallback(CallbackData, prefix="nore_team"):
    teams_amount: int


class SetGameResultCallback(CallbackData, prefix="set_result"):
    game_uuid: UUID4
    team_name: str = None
