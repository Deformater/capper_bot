from data.models import User


def name_validation(name: str) -> bool:
    if len(name.split()) != 4 or len(name) > 255:
        return False

    name, surname, patronymic, group = name.split()

    return f"{name}{surname}{patronymic}".isalpha() and group.isalnum()


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
        result_text += f" {user.username} ({user.balance}💵)\n"
        result_text += f"Кол-во ставок: {user.bet_count}\n"
        result_text += f"% побед: {await user.success_bet_persent()}\n\n"

    result_text += "------------------\n"

    result_text += f"[{current_user_place} место] ({current_user.balance}💵)\n"
    result_text += f"Кол-во ставок: {current_user.bet_count}\n"
    result_text += f"% побед: {await current_user.success_bet_persent()}\n"

    result_text += f"Кол-во участников: {users_total}"

    return result_text
