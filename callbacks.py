from aiogram.filters.callback_data import CallbackData
from pydantic import UUID4


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class GameCallback(CallbackData, prefix="game"):
    game_uuid: UUID4


class BetCallback(CallbackData, prefix="bet"):
    game_uuid: UUID4
    content: str
