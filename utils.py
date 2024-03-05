from datetime import datetime
from data.models import Bet, BetType, Game, User


def validate_bet_size(bet_size: str) -> float | None:
    try:
        bet_size = float(bet_size)
        if 0 < bet_size:
            return bet_size
        else:
            return None
    except:
        return None


def validate_total(total: str) -> bool:
    total_list = total.split("-")
    return (
        (len(total_list) == 2)
        and (validate_bet_size(total_list[0]) is not None)
        and (validate_bet_size(total_list[1]) is not None)
    )


def team_info_validate(info: str) -> bool:
    info_list = info.split("-")
    return (
        (len(info_list) == 2 or len(info_list) == 3 or len(info_list) == 4)
        and (not info_list[0].isdigit())
        and (validate_bet_size(info_list[1]) is not None)
    )


def start_at_validate(date: str) -> datetime | None:
    try:
        now_year = datetime.now().year
        date = datetime.strptime(f"{date}/{now_year}", "%H:%M-%d.%m/%Y")
        return date.replace(year=2024)
    except:
        return None


def game_format_validate(format: str) -> bool:
    return (len(format) == 3) and (format[:2] == "bo") and format[-1].isdigit()


def game_hype_validate(hype: str) -> int | None:
    try:
        hype = int(hype)
        if hype in range(1, 4):
            return hype
        return None
    except:
        return None


def score_validate(score: str) -> bool:
    try:
        score = score.replace(" ", "")
        score_list = list(map(int, score.split(":")))
        return score_list
    except:
        return None


async def generate_rating_text(
    users: list[User], current_user: User, current_user_place: int, users_total: int
) -> str:
    result_text = ""
    for place, user in enumerate(users):
        match place + 1:
            case 1:
                result_text += "🥇"
            case 2:
                result_text += "🥈"
            case 3:
                result_text += "🥉"
            case _:
                result_text += "🏅"
        result_text += f" @{user.username} ({user.balance}💵)\n"
        result_text += f"Кол-во ставок: {user.bet_count}\n"
        result_text += f"% побед: {await user.success_bet_persent}\n\n"

    result_text += "------------------\n"

    result_text += f"{await generate_profile_text(current_user)}\n\n"

    result_text += f"Кол-во участников: {users_total}"

    return result_text


async def generate_profile_text(current_user: User) -> str:
    result_text = ""

    result_text += (
        f"Вы находитесь на {await current_user.place} месте ({current_user.balance}💵)\n"
    )
    result_text += f"Кол-во ставок: {current_user.bet_count}\n"
    result_text += f"Процент побед: {await current_user.success_bet_persent}"

    return result_text


async def generate_bets_history_text(bets: list[Bet]) -> str:
    result_text = ""
    for bet in bets:
        match bet.result:
            case True:
                result_text += "✅"
            case False:
                result_text += "🛑"
            case None:
                result_text += "❔"
        result_text += f"{generate_game_text(await bet.game)}\n"
        match bet.bet_type:
            case BetType.WIN:
                result_text += (
                    f"Победа {bet.team_name} {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
                )
            case BetType.DRAW:
                result_text += f"Ничья {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
            case BetType.DOEBLE_CHANCE:
                result_text += f"Двойной шанс {bet.team_name} {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
            case BetType.FORA_PLUS:
                result_text += f"Фора +1.5 {bet.team_name} {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
            case BetType.FORA_MINUS:
                result_text += f"Фора -1.5 {bet.team_name} {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
            case BetType.TOTAL_BIGGER:
                result_text += (
                    f"Тотал 2.5 Б - {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
                )
            case BetType.TOTAL_LESS:
                result_text += (
                    f"Тотал 2.5 М - {bet.bet_coefficient}⚔️Cумма: {bet.size}\n"
                )

        if bet.result is None:
            result_text += f"Результатов ещё нет("
        else:
            if bet.balance_change > 0:
                result_text += f"Баланс: +{bet.balance_change}"
            else:
                result_text += f"Баланс: {bet.balance_change}"

        result_text += "\n\n"

    return result_text


def generate_game_text(game: Game) -> str:

    result_text = f"{game.starts_at.strftime('%H:%M')}(МСК) {game.first_team_name} ⚔️ {game.second_team_name} {game.format.upper()} {'★' * game.hype}"

    return result_text
