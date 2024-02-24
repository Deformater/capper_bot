from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from callbacks import (
    BetCallback,
    Bo2BetCallback,
    Bo2TeamBetCallback,
    CancelCallback,
    ContinueCallback,
    GameCallback,
    MoreBetCallback,
    SetGameResultCallback,
)
from data.models import Game
from utils import generate_game_text


def base_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Назад", callback_data=CancelCallback())

    return builder


def continue_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Продолжить", callback_data=ContinueCallback())

    return builder.as_markup()


def home_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.button(
        text="🎮Матчи",
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
    if game.format == "bo2":
        return bo2_bet_keyboard(game)
    return base_bet_keyboard(game)


def base_bet_keyboard(game: Game):
    builder = InlineKeyboardBuilder()
    first_team_info = f"{game.first_team_name} - {game.first_team_coefficient}"
    builder.button(
        text=first_team_info,
        callback_data=BetCallback(
            game_uuid=game.uuid, content=first_team_info, bet_type="WIN"
        ),
    )
    second_team_info = f"{game.second_team_name} - {game.second_team_coefficient}"
    builder.button(
        text=second_team_info,
        callback_data=BetCallback(
            game_uuid=game.uuid, content=second_team_info, bet_type="WIN"
        ),
    )
    builder.adjust(2)

    return builder.as_markup()


def bo2_bet_keyboard(game: Game):
    builder = InlineKeyboardBuilder()
    first_team_info = f"{game.first_team_name}"
    builder.button(
        text=first_team_info,
        callback_data=Bo2BetCallback(game_uuid=game.uuid, content=first_team_info),
    )
    draw_info = f"ничья - {game.draw_coefficient}"
    builder.button(
        text=draw_info,
        callback_data=BetCallback(
            game_uuid=game.uuid, content=draw_info, bet_type="DRAW"
        ),
    )
    second_team_info = f"{game.second_team_name}"
    builder.button(
        text=second_team_info,
        callback_data=Bo2BetCallback(game_uuid=game.uuid, content=second_team_info),
    )
    builder.adjust(3)

    return builder.as_markup()


def bo2_team_bet_keyboard(
    game: Game, win_coefficient: float, double_chance_coefficient: float
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Победа - {win_coefficient}",
        callback_data=Bo2TeamBetCallback(
            game_uuid=game.uuid, bet_type="WIN", bet_coefficient=win_coefficient
        ),
    )
    builder.button(
        text=f"Двойной шанс - {double_chance_coefficient}",
        callback_data=Bo2TeamBetCallback(
            game_uuid=game.uuid,
            bet_type="D_CH",
            bet_coefficient=double_chance_coefficient,
        ),
    )
    builder.adjust(2)

    return builder.as_markup()


def admin_game_keyboard(game: Game):
    builder = InlineKeyboardBuilder()

    first_team_name = game.first_team_name
    second_team_name = game.second_team_name

    if game.winner == first_team_name:
        first_team_name = f"✅{game.first_team_name}"
    if game.winner == second_team_name:
        second_team_name = f"✅{second_team_name}"

    builder.button(
        text=first_team_name,
        callback_data=SetGameResultCallback(
            game_uuid=game.uuid, team_name=game.first_team_name
        ),
    )

    builder.button(
        text=second_team_name,
        callback_data=SetGameResultCallback(
            game_uuid=game.uuid, team_name=game.second_team_name
        ),
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


def cancel_bet_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Назад")
    return builder.as_markup(resize_keyboard=True)
