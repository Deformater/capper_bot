from aiogram.filters.callback_data import CallbackData
from pydantic import UUID4


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class GamesCallback(CallbackData, prefix="games"):
    pass


class GameCallback(CallbackData, prefix="game"):
    game_uuid: UUID4


# class ActionCallback(CallbackData, prefix="action"):
#     action: str
