from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from callbacks import CancelCallback, GamesCallback, GameCallback


def base_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Назад", callback_data=CancelCallback())

    return builder


def home_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.button(text="⚽️Матчи")
    builder.button(text="📈История ставок")
    builder.button(text="🙍‍♂️Профиль")
    builder.button(text="💬Чат")
    builder.button(text="🗓Активный сезон")
    builder.button(text="📝Условия")
    builder.button(text="🏆Рейтинг")
    builder.adjust(2, 2, 3)

    return builder.as_markup()


def games_keyboard(games: list):
    builder = InlineKeyboardBuilder()

    for game in games:
        btn_text = f"{game.starts_at.strftime('%H:%M')}(МСК) {game.first_team_name} 🆚 {game.second_team_name} {game.format} {'*' * game.hype}"
        builder.button(
            text=btn_text,
            callback_data=GameCallback(game_uuid=game.uuid),
        )
        builder.adjust(1)
    builder.attach(base_keyboard())

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
