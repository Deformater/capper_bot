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

from keyboards import bet_keyboard, home_keyboard, games_keyboard
from callbacks import BetCallback, CancelCallback, GameCallback
from data.models import Bet, Game, User

from utils import (
    generate_rating_text,
    generate_profile_text,
    generate_game_text,
    validate_bet_size,
)
import settings


dlg_router = Router()


class Form(StatesGroup):
    bet = State()


# @dlg_router.error(ExceptionTypeFilter(KeyError), F.update.query.as_("query"))
# async def error_handler(event: ErrorEvent, query: CallbackQuery) -> None:
#         await query.message.answer("Что-то пошло не так, перезапустите бота /start")


@dlg_router.message(CommandStart())
async def command_start(message: Message) -> None:

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
    if message.chat.id in settings.ADMIN_IDS:
        chats = []
        args = command.args
        if args is not None:
            for chat in chats:
                try:
                    await message.bot.send_message(chat.tg_id, args)
                except TelegramForbiddenError:
                    continue


@dlg_router.message(F.text == "⚽️Матчи")
async def games_handler(message: Message) -> None:
    games = await Game.all()
    today_games = []
    for game in games:
        if game.starts_at.date() == datetime.date.today():
            today_games.append(game)

    if today_games:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Интересные матчи сегодня:",
            reply_markup=games_keyboard(today_games),
        )
    else:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Сегодня нет игр(",
            reply_markup=games_keyboard(today_games),
        )


@dlg_router.message(F.text == "🏆Рейтинг")
async def rating_handler(message: Message) -> None:
    users = await User.all().order_by("-balance")
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
    result_text = "Хочешь сделать ставку?\n\n"
    result_text += generate_game_text(game)
    await query.message.edit_text(text=result_text, reply_markup=bet_keyboard(game))


@dlg_router.callback_query(BetCallback.filter())
async def bet_handler(
    query: CallbackQuery, callback_data: BetCallback, state: FSMContext
) -> None:
    uuid = callback_data.game_uuid

    await state.clear()
    await state.set_state(Form.bet)
    await state.update_data(
        bet=callback_data.content,
        game_uuid=str(uuid),
        bet_content=callback_data.content,
    )

    game = await Game.get(uuid=uuid)

    result_text = "Хочешь сделать ставку?\n\n"
    result_text += generate_game_text(game) + "\n"
    result_text += f"Ставка на победу {callback_data.content}\n\n"

    user = await User.get(tg_id=query.message.chat.id)

    result_text += f"Баланс {user.balance}💵\n"
    result_text += f"Введи сумму ставки:"

    await query.message.edit_text(text=result_text)


@dlg_router.message(Form.bet)
async def process_name(message: Message, state: FSMContext) -> None:
    if (bet_size := validate_bet_size(message.text)) is not None:
        data = await state.get_data()

        user = await User.get(tg_id=message.chat.id)
        game = await Game.get(uuid=data["game_uuid"])
        team_name = data["bet_content"].split()[0]

        await Bet.create(size=bet_size, user=user, game=game, team_name=team_name)
        await state.clear()

        await message.answer(f"Вы успешно поставили на {data['bet']}")
    else:
        await message.answer("Неверный формат ввода")


# @dlg_router.callback_query(CancelCallback.filter(), Form.date)
# async def cancel_laba_handler(
#     query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
# ) -> None:
#     await state.set_state(Form.laba)
#     await query.message.edit_text(
#         text=f"Выберите предмет", reply_markup=laba_keyboard()
#     )


# @dlg_router.callback_query(CancelCallback.filter(), Form.action)
# async def cancel_date_handler(
#     query: CallbackQuery, callback_data: LabaCallback, state: FSMContext
# ) -> None:
#     await state.set_state(Form.date)
#     await query.message.edit_text(
#         text=f"Выберите дату сдачи лабораторной", reply_markup=date_keyboard()
#     )
