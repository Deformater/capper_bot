from data.models import Game, User


def validate_bet_size(bet_size: str) -> float | None:
    try:
        bet_size = float(bet_size)
        if 0 < bet_size:
            return bet_size
        else:
            return None
    except:
        return None


async def generate_rating_text(
    users: list[User], current_user: User, current_user_place: int, users_total: int
) -> str:
    result_text = ""
    for place, user in enumerate(users):
        match place:
            case 1:
                result_text += "🥇"
            case 2:
                result_text += "🥈"
            case 3:
                result_text += "🥉"
            case _:
                result_text += "🏅"
        # persentage = await user.success_bet_persent()
        result_text += f" @{user.username} ({user.balance}💵)\n"
        result_text += f"Кол-во ставок: {user.bet_count}\n"
        result_text += f"% побед: {await user.success_bet_persent}\n\n"

    result_text += "------------------\n"

    result_text += (
        f"[{current_user_place} место] {user.username} ({current_user.balance}💵)\n"
    )
    result_text += f"Кол-во ставок: {current_user.bet_count}\n"
    result_text += f"% побед: {await current_user.success_bet_persent}\n"

    result_text += f"Кол-во участников: {users_total}"

    return result_text


async def generate_profile_text(current_user: User) -> str:
    result_text = ""

    result_text += f"[{await current_user.place} место] {current_user.username} ({current_user.balance}💵)\n"
    result_text += f"Кол-во ставок: {current_user.bet_count}\n"
    result_text += f"% побед: {await current_user.success_bet_persent}"

    return result_text


def generate_game_text(game: Game) -> str:

    result_text = f"{game.starts_at.strftime('%H:%M')}(МСК) {game.first_team_name} 🆚 {game.second_team_name} {game.format} {'*' * game.hype}"

    return result_text
