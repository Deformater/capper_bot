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
import pytz

from keyboards import (
    admin_game_keyboard,
    bet_history_keyboard,
    bet_keyboard,
    bo2_bet_keyboard,
    bo2_team_bet_keyboard,
    cancel_bet_keyboard,
    continue_keyboard,
    home_keyboard,
    games_keyboard,
    chat_link_keyboard,
)
from callbacks import (
    BetCallback,
    Bo2BetCallback,
    Bo2TeamBetCallback,
    CancelCallback,
    ContinueCallback,
    GameCallback,
    MoreBetCallback,
    MoreTeamCallback,
    SetGameResultCallback,
)
from data.models import Bet, BetType, Game, User

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

    if message.chat.username is None:
        username = str(message.chat.id)
    else:
        username = message.chat.username

    user = await User.get_or_create(tg_id=message.chat.id, username=username)

    text = f"""<i>Привет! Ты попал в бот "Турнир прогнозистов" на DreamLeague Season 22, здесь все участники соревнуются между собой за главные призы, 1 место - $250 , 2 место - $100, 3 место - $50. Изначальный баланс : 5.000, собственно у кого в конце будет самый большой баланс - забирает главный приз, а отслеживать свое место вы можете во вкладке "Рейтинг", присоединяйся к нам и может именно ты заберешь главный приз!</i>

<b>Все абсолютно бесплатно, единственное условие для участия - подписка на <a href="{settings.GROUP_NAME}">наш канал</a></b>

<a href="{settings.GROUP_NAME}">Наш канал</a>
    """

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=continue_keyboard(),
        disable_web_page_preview=True,
    )


@dlg_router.callback_query(ContinueCallback.filter())
async def game_handler(
    query: CallbackQuery, callback_data: GameCallback, state: FSMContext
) -> None:
    user = await User.get(tg_id=query.message.chat.id)
    user_channel_status = await query.bot.get_chat_member(
        chat_id=settings.GROUP_ID, user_id=query.message.chat.id
    )
    user.is_subscripe = not (user_channel_status.status == "left")
    await user.save()

    text = await generate_profile_text(user)
    await query.message.answer(text, reply_markup=home_keyboard(), parse_mode="HTML")


@dlg_router.message(Command("admin"))
async def command_admin(message: Message, command: CommandObject) -> None:
    user = await User.get(tg_id=message.chat.id)
    if not user.is_admin:
        return

    users = await User.all()
    args = command.args
    if args is not None:
        for user in users:
            try:
                await message.bot.send_message(user.tg_id, args)
            except TelegramForbiddenError:
                continue


@dlg_router.message(Command("set_admin"))
async def command_admin(message: Message, command: CommandObject) -> None:
    user = await User.get(tg_id=message.chat.id)
    if not user.is_admin:
        return

    args = command.args
    if args is not None:
        admin_user = await User.filter(username=args).first()
        if admin_user:
            admin_user.is_admin = True
            await admin_user.save()
            await message.answer(
                f"Пользователь {admin_user.username} успешно добавлен в администраторы"
            )
        else:
            await message.answer(f"Пользователь {args} не найден")


@dlg_router.message(Command("del_admin"))
async def command_admin(message: Message, command: CommandObject) -> None:
    user = await User.get(tg_id=message.chat.id)
    if not user.is_admin:
        return

    args = command.args
    if args is not None:
        admin_user = await User.filter(username=args).first()
        if admin_user:
            admin_user.is_admin = False
            await admin_user.save()
            await message.answer(
                f"Пользователь {admin_user.username} успешно удалён из администраторов"
            )
        else:
            await message.answer(f"Пользователь {args} не найден")


@dlg_router.message(F.text == "🎮Матчи")
async def games_handler(message: Message) -> None:
    games = await Game.filter(first_team_score=None).order_by("starts_at")
    user = await User.get(tg_id=message.chat.id)

    today_games = []
    for game in games:
        if user.is_admin:
            today_games.append(game)
            continue

        if (
            game.starts_at - datetime.timedelta(hours=3)
        ) >= datetime.datetime.now().replace(tzinfo=pytz.UTC):
            today_games.append(game)

    if today_games:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Предстоящие матчи:",
            reply_markup=games_keyboard(
                today_games[:5], teams_amount=5, more_games=(len(today_games) > 5)
            ),
        )
    else:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Пока нет предстоящих матчей(",
        )


@dlg_router.callback_query(MoreTeamCallback.filter())
async def more_games_handler(
    query: CallbackQuery, callback_data: GameCallback, state: FSMContext
) -> None:
    games = await Game.filter(first_team_score=None).order_by("starts_at")
    teams_amount = callback_data.teams_amount
    teams_amount += 5

    user = await User.get(tg_id=query.message.chat.id)

    today_games = []
    for game in games:
        if user.is_admin:
            today_games.append(game)
            continue
        if (
            game.starts_at - datetime.timedelta(hours=3)
        ) >= datetime.datetime.now().replace(tzinfo=pytz.UTC):
            today_games.append(game)

    if today_games:
        await query.message.edit_text(
            text=f"Предстоящие матчи:",
            reply_markup=games_keyboard(
                today_games[:teams_amount],
                teams_amount,
                more_games=(len(today_games) > teams_amount),
            ),
        )
    else:
        await query.message.edit_text(
            text=f"Пока нет предстоящих матчей(",
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
    user = await User.get(tg_id=query.message.chat.id)

    if user.is_admin:
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
        await state.update_data(game_uuid=str(uuid))

        return

    result_text = "Хочешь сделать ставку?\n\n"
    result_text += generate_game_text(game)
    await query.message.edit_text(text=result_text, reply_markup=bet_keyboard(game))


@dlg_router.callback_query(CancelCallback.filter())
async def cancel_handler(
    query: CallbackQuery, callback_data: GameCallback, state: FSMContext
) -> None:
    games = await Game.filter(first_team_score=None).order_by("starts_at")
    user = await User.get(tg_id=query.message.chat.id)

    today_games = []
    for game in games:
        if user.is_admin:
            today_games.append(game)
            continue
        if (
            game.starts_at - datetime.timedelta(hours=3)
        ) >= datetime.datetime.now().replace(tzinfo=pytz.UTC):
            today_games.append(game)

    if today_games:
        await query.message.edit_text(
            text=f"Предстоящие матчи:",
            reply_markup=games_keyboard(
                today_games[:5], 5, more_games=(len(today_games) > 5)
            ),
        )
    else:
        await query.message.edit_text(
            text=f"Пока нет предстоящих матчей(",
        )


@dlg_router.message(GameAdmin.score)
async def process_game_score(message: Message, state: FSMContext) -> None:
    if (score := score_validate(message.text)) is not None:
        data = await state.get_data()
        game = await Game.get(uuid=data["game_uuid"]).prefetch_related("bets__user")
        await game.set_score(score)
        await message.answer("Итоговый счёт установлен", reply_markup=home_keyboard())

        for bet in game.bets:
            try:
                result_text = "Результат ставки:\n\n"
                result_text += await generate_bets_history_text([bet])
                await message.bot.send_message(bet.user.tg_id, result_text)
            except TelegramForbiddenError:
                continue
        await state.clear()

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

        game = await Game.get(uuid=data["game_uuid"])
        user = await User.get(tg_id=message.chat.id).prefetch_related(
            Prefetch("bets", queryset=Bet.filter(game=game))
        )

        if user.balance < bet_size:
            await message.answer("У вас недостаточно средств")
            return

        if bet_size > 1000:
            await message.answer("Максимальная ставка - 1000💵")
            return

        team_name, bet_coefficient = data["bet_content"].split(" - ")
        if team_name == "Ничья":
            team_name = None

        if len(user.bets) > 0:
            for bet in user.bets:
                if (bet.team_name == team_name) and (
                    bet.bet_type == BetType(data["bet_type"])
                ):
                    await message.answer(
                        f"Вы уже поставили на эту котировку",
                        reply_markup=home_keyboard(),
                    )
                    await state.clear()
                    return

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
        text="""В нашем боте каждый из участников может посоревноваться за призы(<b>250$</b> - 1 место, <b>100$</b> - 2 место, <b>50$</b> - 3 место)

Все что от вас требуется - это ежедневно делать прогнозы в нашем боте на матчи DreamLeague S22, в итоге после финала турнира трое лучших прогнозистов смогут забрать свои призы!

Отслеживать свое место на данный момент вы можете во вкладке '🏆Рейтинг', желаем удачи!

ℹ️ <i>Если возникли проблемы(попробуйте сначала перезапустить /start), не помогло пишите: @bpmanager1</i>
""",
        parse_mode="HTML",
        reply_markup=home_keyboard(),
    )


@dlg_router.message(F.text == "🗣Условия")
async def bot_info_handler(message: Message) -> None:
    text = (
        f"""1️⃣ Подписаться на наш канал <a href="{settings.GROUP_NAME}">BetPulse</a>"""
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=home_keyboard(),
        disable_web_page_preview=True,
    )


@dlg_router.message(F.text == "💬Чат")
async def chat_handler(message: Message):
    await message.bot.send_message(
        chat_id=message.chat.id,
        text="Нажмите на кнопку ниже, чтобы присоединиться к нашему чату:",
        reply_markup=chat_link_keyboard(),
    )


async def interesting_games(bot):
    games = await Game.filter(
        first_team_score=None,
        starts_at__gte=datetime.datetime.now() + datetime.timedelta(hours=3),
        hype__gt=1,
    ).order_by("starts_at")
    today_games = []
    result_text = "Интересные матчи сегодня:"
    for game in games:
        if game.starts_at.date() == datetime.date.today():
            today_games.append(game)

    users = await User.all()
    for user in users:
        try:
            await bot.send_message(
                user.tg_id,
                result_text,
                reply_markup=games_keyboard(
                    today_games, teams_amount=5, more_games=True
                ),
            )
        except TelegramForbiddenError:
            continue
