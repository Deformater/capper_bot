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
    home_keyboard,
    games_keyboard,
    chat_link_keyboard,
)
from callbacks import (
    BetCallback,
    CancelCallback,
    GameCallback,
    MoreBetCallback,
    SetGameResultCallback,
)
from data.models import Bet, Game, User

from utils import (
    game_format_validate,
    game_hype_validate,
    generate_rating_text,
    generate_profile_text,
    generate_game_text,
    start_at_validate,
    team_info_validate,
    validate_bet_size,
    generate_bets_history_text,
)

from tortoise.query_utils import Prefetch
import settings


game_add_router = Router()


class GameAdd(StatesGroup):
    first_team_info = State()
    second_team_info = State()
    starts_at = State()
    format = State()
    hype = State()


@game_add_router.message(Command("add_game"))
async def command_admin(
    message: Message, command: CommandObject, state: FSMContext
) -> None:
    if message.chat.id not in settings.ADMIN_IDS:
        return

    await state.clear()
    result_text = "Введите данные первой команды:\n"
    result_text += "Формат ввода: <b>Название команды-коэффициент</b>"
    await message.bot.send_message(
        chat_id=message.chat.id, text=result_text, parse_mode="HTML"
    )
    await state.clear()

    await state.set_state(GameAdd.first_team_info)


@game_add_router.message(GameAdd.first_team_info)
async def process_first_team_info(message: Message, state: FSMContext) -> None:
    if not team_info_validate(message.text):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return

    name, coeff = message.text.split("-")
    coeff = float(coeff)

    await state.update_data(first_team_name=name, first_team_coefficient=coeff)
    result_text = "Введите данные Второй команды:\n"
    result_text += "Формат ввода: <b>Название команды-коэффициент</b>"
    await message.bot.send_message(
        chat_id=message.chat.id, text=result_text, parse_mode="HTML"
    )
    await state.set_state(GameAdd.second_team_info)


@game_add_router.message(GameAdd.second_team_info)
async def process_second_team_info(message: Message, state: FSMContext) -> None:
    if not team_info_validate(message.text):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return

    name, coeff = message.text.split("-")
    coeff = float(coeff)

    await state.update_data(second_team_name=name, second_team_coefficient=coeff)
    result_text = "Введите формат игры:\n"
    result_text += "Формат ввода: bo3"
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
    )
    await state.set_state(GameAdd.format)


@game_add_router.message(GameAdd.format)
async def process_format(message: Message, state: FSMContext) -> None:
    if not game_format_validate(message.text):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return
    await state.update_data(format=message.text)
    result_text = "Введите уровень интересности\n"
    result_text += "Формат ввода: число 1-3"
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
    )
    await state.set_state(GameAdd.hype)


@game_add_router.message(GameAdd.hype)
async def process_format(message: Message, state: FSMContext) -> None:

    if (hype := game_hype_validate(message.text)) is None:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return

    await state.update_data(hype=hype)
    result_text = "Введите время начала игры:\n"
    result_text += "14:35-24.02"
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
    )
    await state.set_state(GameAdd.starts_at)


@game_add_router.message(GameAdd.starts_at)
async def process_start_time(message: Message, state: FSMContext) -> None:
    if (date := start_at_validate(message.text)) is None:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return
    data = await state.get_data()
    game = await Game.create(**data, starts_at=date)
    result_text = "Игра успешно добавлена\n"
    result_text += generate_game_text(game)
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
    )
    await state.clear()
