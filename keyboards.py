from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from callbacks import BetCallback, CancelCallback, GameCallback, MoreBetCallback
from data.models import Game
from utils import generate_game_text


def base_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Назад", callback_data=CancelCallback())

    return builder


def home_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.button(
        text="⚽️Матчи",
    )
    builder.button(text="📈История ставок")
    builder.button(text="🙍‍♂️Профиль")
    builder.button(text="💬Чат")
    builder.button(text="📝О боте")
    builder.button(text="🏆Рейтинг")
    builder.adjust(2, 2, 2)

    return builder.as_markup()


def games_keyboard(games: list):
    builder = InlineKeyboardBuilder()

    for game in games:
        btn_text = generate_game_text(game)
        builder.button(
            text=btn_text,
            callback_data=GameCallback(game_uuid=game.uuid),
        )
        builder.adjust(1)

    return builder.as_markup()


def bet_keyboard(game: Game):
    builder = InlineKeyboardBuilder()
    first_team_info = f"{game.first_team_name} - {game.first_team_coefficient}"
    builder.button(
        text=first_team_info,
        callback_data=BetCallback(game_uuid=game.uuid, content=first_team_info),
    )
    second_team_info = f"{game.second_team_name} - {game.second_team_coefficient}"
    builder.button(
        text=second_team_info,
        callback_data=BetCallback(game_uuid=game.uuid, content=second_team_info),
    )
    builder.adjust(2)

    return builder.as_markup()


def chat_link_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Присоединиться к чату", url="https://t.me/+WkoR_WEMA9tlNTcy")
    return builder.as_markup()


def bet_history_keyboard(bets_amount):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Больше ставок",
        callback_data=MoreBetCallback(bets_amount=bets_amount),
    )
    return builder.as_markup()


# def date_keyboard():
#     builder = InlineKeyboardBuilder()

#     current_date = datetime.datetime.now().date()
#     date_delta = datetime.timedelta(days=30)
#     end_date = current_date + date_delta

#     while current_date < end_date:
#         builder.button(
#             text=current_date.strftime("%d/%m"),
#             callback_data=DateCallback(date=current_date.strftime("%d/%m")),
#         )
#         builder.adjust(6)
#         current_date += datetime.timedelta(days=1)

#     builder.attach(base_keyboard())

#     return builder.as_markup()


# def action_keyboard():
#     builder = InlineKeyboardBuilder()

#     builder.button(text="Записаться", callback_data=ActionCallback(action="join"))

#     builder.attach(base_keyboard())
#     builder.adjust(2, 1)

#     return builder.as_markup()
