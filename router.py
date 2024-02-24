import datetime

from aiogram import Router, html, F
from aiogram.filters import CommandStart, Command, CommandObject, ExceptionTypeFilter
from aiogram.types import (
    Message,
    InlineQuery,
    CallbackQuery,
    ReplyKeyboardRemove,
    ErrorEvent,
    ChatMemberLeft,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from keyboards import (
    admin_game_keyboard,
    bet_history_keyboard,
    bet_keyboard,
    bo2_bet_keyboard,
    bo2_team_bet_keyboard,
    cancel_bet_keyboard,
    home_keyboard,
    games_keyboard,
    chat_link_keyboard,
)
from callbacks import (
    BetCallback,
    Bo2BetCallback,
    Bo2TeamBetCallback,
    CancelCallback,
    GameCallback,
    MoreBetCallback,
    SetGameResultCallback,
)
from data.models import Bet, Game, User

from utils import (
    generate_rating_text,
    generate_profile_text,
    generate_game_text,
    score_validate,
    start_at_validate,
    team_info_validate,
    validate_bet_size,
    generate_bets_history_text,
)

from tortoise.query_utils import Prefetch
import settings


dlg_router = Router()


class Form(StatesGroup):
    bet = State()


class GameAdmin(StatesGroup):
    score = State()


@dlg_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:

    await state.clear()

    user = await User.get_or_create(
        tg_id=message.chat.id, username=message.chat.username
    )
    user = user[0]
    user_channel_status = await message.bot.get_chat_member(
        chat_id=settings.GROUP_NAME, user_id=message.chat.id
    )
    user.is_subscripe = not (user_channel_status.status == "left")
    await user.save()

    if user.is_subscripe:
        await message.answer(
            f"Вы подписаны на {settings.GROUP_NAME}",
            reply_markup=home_keyboard(),
        )
    else:
        await message.answer(
            f"Вы не подписаны на группу {settings.GROUP_NAME}",
            reply_markup=ReplyKeyboardRemove(),
        )


@dlg_router.message(Command("admin"))
async def command_admin(message: Message, command: CommandObject) -> None:
    if message.chat.id not in settings.ADMIN_IDS:
        return

    users = await User.all()
    args = command.args
    if args is not None:
        for user in users:
            try:
                await message.bot.send_message(user.tg_id, args)
            except TelegramForbiddenError:
                continue


@dlg_router.message(F.text == "⚽️Матчи")
async def games_handler(message: Message) -> None:
    games = await Game.filter(first_team_score=None).order_by("starts_at")
    today_games = []
    for game in games:
        if game.starts_at.date() >= datetime.date.today():
            today_games.append(game)

    if today_games:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Предстоящие матчи:",
            reply_markup=games_keyboard(today_games),
        )
    else:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Пока нет предстоящих матчей(",
            reply_markup=games_keyboard(today_games),
        )


@dlg_router.message(F.text == "🏆Рейтинг")
async def rating_handler(message: Message) -> None:
    users = await User.all().order_by("-_balance")
    current_user = await User.get(tg_id=message.chat.id)
    current_user_place = users.index(current_user) + 1

    result_text = await generate_rating_text(
        users=users[:5],
        current_user=current_user,
        current_user_place=current_user_place,
        users_total=len(users),
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
        reply_markup=home_keyboard(),
    )


@dlg_router.message(F.text == "🙍‍♂️Профиль")
async def profile_handler(message: Message) -> None:
    current_user = await User.get(tg_id=message.chat.id)

    result_text = await generate_profile_text(
        current_user=current_user,
    )

    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
        reply_markup=home_keyboard(),
    )


@dlg_router.callback_query(GameCallback.filter())
async def game_handler(
    query: CallbackQuery, callback_data: GameCallback, state: FSMContext
) -> None:
    uuid = callback_data.game_uuid
    game = await Game.get(uuid=uuid)
    await state.update_data(game_uuid=str(uuid))

    if query.message.chat.id in settings.ADMIN_IDS:
        result_text = "Админ панель игры:\n"
        result_text += f"{generate_game_text(game)}\n"
        result_text += "Введи итоговый счёт в формате:\n"
        result_text += "1:2"
        await query.bot.send_message(
            chat_id=query.message.chat.id,
            text=result_text,
            reply_markup=cancel_bet_keyboard(),
        )
        await state.set_state(GameAdmin.score)
        return

    result_text = "Хочешь сделать ставку?\n\n"
    result_text += generate_game_text(game)
    await query.message.edit_text(text=result_text, reply_markup=bet_keyboard(game))


@dlg_router.message(GameAdmin.score)
async def process_game_score(message: Message, state: FSMContext) -> None:
    if (score := score_validate(message.text)) is not None:
        data = await state.get_data()
        game = await Game.get(uuid=data["game_uuid"]).prefetch_related("bets__user")
        await game.set_score(score)
        await message.answer("Итоговый счёт установлен", reply_markup=home_keyboard())
        await state.clear()

        for bet in game.bets:
            try:
                result_text = "Результат ставки:\n\n"
                result_text += await generate_bets_history_text([bet])
                await message.bot.send_message(bet.user.tg_id, result_text)
            except TelegramForbiddenError:
                continue

    else:
        if message.text == "Назад":
            await state.clear()
            await message.answer(
                "Итоговый счёт не установлен", reply_markup=home_keyboard()
            )
            return

        await message.answer("Неверный формат ввода")


@dlg_router.callback_query(BetCallback.filter())
async def bet_handler(
    query: CallbackQuery, callback_data: BetCallback, state: FSMContext
) -> None:
    uuid = callback_data.game_uuid

    game = await Game.get(uuid=uuid)

    result_text = "Хочешь сделать ставку?\n\n"
    result_text += generate_game_text(game) + "\n"
    if callback_data.bet_type == "DRAW":
        result_text += f"Ставка на {callback_data.content}\n\n"
    else:
        result_text += f"Ставка на победу {callback_data.content}\n\n"

    user = await User.get(tg_id=query.message.chat.id)

    result_text += f"Баланс {user.balance}💵\n"
    result_text += f"Введи сумму ставки:"
    await state.set_state(Form.bet)
    await state.update_data(
        game_uuid=str(uuid),
        bet_content=callback_data.content,
        bet_type=callback_data.bet_type,
    )

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text=result_text,
        reply_markup=cancel_bet_keyboard(),
    )


@dlg_router.callback_query(Bo2BetCallback.filter())
async def bet_handler(
    query: CallbackQuery, callback_data: Bo2BetCallback, state: FSMContext
) -> None:
    uuid = callback_data.game_uuid

    game = await Game.get(uuid=uuid)

    await state.update_data(team_name=callback_data.content)

    result_text = f"Выбрана комнда {callback_data.content}\n"
    result_text += "Выберите тип ставки:"
    if callback_data.content == game.first_team_name:
        win_coeff, double_chance_coeff = (
            game.first_team_coefficient,
            game.first_team_double_chance,
        )
    else:
        win_coeff, double_chance_coeff = (
            game.second_team_coefficient,
            game.second_team_double_chance,
        )
    await query.message.edit_text(
        text=result_text,
        reply_markup=bo2_team_bet_keyboard(game, win_coeff, double_chance_coeff),
    )
    return


@dlg_router.callback_query(Bo2TeamBetCallback.filter())
async def bo2_team_bet_handler(
    query: CallbackQuery, callback_data: Bo2TeamBetCallback, state: FSMContext
) -> None:
    data = await state.get_data()
    team_name = data["team_name"]
    uuid = callback_data.game_uuid

    await state.clear()

    game = await Game.get(uuid=uuid)
    content = f"{team_name} - {callback_data.bet_coefficient}"

    result_text = "Хочешь сделать ставку?\n\n"
    result_text += generate_game_text(game) + "\n"
    if callback_data.bet_type == "D_CH":
        result_text += f"Ставка на двойной шанс {content}\n\n"
    else:
        result_text += f"Ставка на победу {content}\n\n"

    user = await User.get(tg_id=query.message.chat.id)

    result_text += f"Баланс {user.balance}💵\n"
    result_text += f"Введи сумму ставки:"

    await state.set_state(Form.bet)
    await state.update_data(
        game_uuid=str(uuid),
        bet_content=content,
        bet_type=callback_data.bet_type,
    )

    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text=result_text,
        reply_markup=cancel_bet_keyboard(),
    )


@dlg_router.message(Form.bet)
async def process_bet_size(message: Message, state: FSMContext) -> None:
    if (bet_size := validate_bet_size(message.text)) is not None:
        data = await state.get_data()

        user = await User.get(tg_id=message.chat.id)
        game = await Game.get(uuid=data["game_uuid"])

        if user.balance < bet_size:
            await message.answer("У вас недостаточно средств")
            return

        if bet_size > 1000:
            await message.answer("Максимальная ставка - 1000💵")
            return

        team_name, bet_coefficient = data["bet_content"].split(" - ")
        if team_name == "Ничья":
            team_name = None

        await Bet.create(
            size=bet_size,
            user=user,
            game=game,
            team_name=team_name,
            bet_coefficient=bet_coefficient,
            bet_type=data["bet_type"],
        )
        user.balance -= bet_size
        user.bet_count += 1
        await user.save()

        await state.clear()

        await message.answer(
            f"Вы успешно поставили на {data['bet_content']}",
            reply_markup=home_keyboard(),
        )
    else:
        if message.text == "Назад":
            await state.clear()
            await message.answer("Ставка отменена", reply_markup=home_keyboard())
            return

        await message.answer("Неверный формат ввода")


@dlg_router.message(F.text == "📈История ставок")
async def bet_history_handler(message: Message):
    user = await User.get(tg_id=message.chat.id).prefetch_related(
        Prefetch("bets", queryset=Bet.all().order_by("-created_at"))
    )

    if len(user.bets) == 0:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="У вас пока нет ставок(",
        )
        return

    result_text = "📈История ставок:\n\n"
    result_text += await generate_bets_history_text(user.bets[:5])
    if len(user.bets) > 5:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=result_text,
            reply_markup=bet_history_keyboard(5),
        )
    else:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=result_text,
        )


@dlg_router.callback_query(MoreBetCallback.filter())
async def bet_history_handler(
    query: CallbackQuery, callback_data: MoreBetCallback
) -> None:
    user = await User.get(tg_id=query.message.chat.id).prefetch_related(
        Prefetch("bets", queryset=Bet.all().order_by("-created_at"))
    )
    bets_amount = callback_data.bets_amount + 5
    result_text = "📈История ставок:\n\n"
    result_text += await generate_bets_history_text(user.bets[:bets_amount])
    if callback_data.bets_amount < 30 and bets_amount < len(user.bets):
        await query.message.edit_text(
            text=result_text,
            reply_markup=bet_history_keyboard(bets_amount + 5),
        )
    else:
        await query.message.edit_text(
            text=result_text,
        )


@dlg_router.message(F.text == "📝О боте")
async def bot_info_handler(message: Message) -> None:
    await message.bot.send_message(
        chat_id=message.chat.id,
        text="""
            В нашем боте каждый из участников может посоревноваться за призы(<b>250$</b> - 1 место, <b>100$ - 2 место</b>, <b>50$</b> - 3 место)

            Все что вам нужно делать это ежедневно делать прогнозы в нашем боте на матчи DreamLeague S22, в итоге после финала турнира трое лучших прогнозистов смогут забрать свои призы!!

            Отслеживать свое место на данный момент вы можете во вкладке '🏆Рейтинг', желаем удачи!
            """,
        parse_mode="HTML",
        reply_markup=home_keyboard(),
    )


@dlg_router.message(F.text == "💬Чат")
async def chat_handler(message: Message):
    await message.bot.send_message(
        chat_id=message.chat.id,
        text="Нажмите на кнопку ниже, чтобы присоединиться к нашему чату:",
        reply_markup=chat_link_keyboard(),
    )
