from aiogram.filters.callback_data import CallbackData


class CancelCallback(CallbackData, prefix="cancel"):
    pass


class GameCallback(CallbackData, prefix="game"):
    pass


# class DateCallback(CallbackData, prefix="date"):
#     date: str


# class ActionCallback(CallbackData, prefix="action"):
#     action: str
