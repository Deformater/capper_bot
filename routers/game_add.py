import datetime

from aiogram import Router, html, F
from aiogram.filters import Command, CommandObject, ExceptionTypeFilter
from aiogram.types import Message

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from data.models import Bet, Game, User

from utils import (
    game_format_validate,
    game_hype_validate,
    generate_game_text,
    start_at_validate,
    team_info_validate,
    validate_bet_size,
    validate_total,
)

from tortoise.query_utils import Prefetch
import settings


game_add_router = Router()


class GameAdd(StatesGroup):
    first_team_info = State()
    second_team_info = State()
    starts_at = State()
    format = State()
    draw = State()
    total = State()
    hype = State()


@game_add_router.message(Command("add_game"))
async def command_admin(
    message: Message, command: CommandObject, state: FSMContext
) -> None:
    user = await User.get(tg_id=message.chat.id)
    if not user.is_admin:
        return

    await state.clear()
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

    result_text = "Введите данные первой команды:\n"

    data = await state.get_data()

    if data["format"] == "bo2":
        result_text += "Формат ввода: <b>Название команды-коэффициент победы-коэффициент двойного шанса</b>"
    elif data["format"] == "bo3":
        result_text += "Формат ввода:\n <b>Название команды-коэффициент победы-фора+1.5-фора-1.5</b>"
    else:
        result_text += "Формат ввода: <b>Название команды-коэффициент</b>"

    await message.bot.send_message(
        chat_id=message.chat.id, text=result_text, parse_mode="HTML"
    )

    await state.set_state(GameAdd.first_team_info)


@game_add_router.message(GameAdd.first_team_info)
async def process_first_team_info(message: Message, state: FSMContext) -> None:
    if not team_info_validate(message.text):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return

    data = await state.get_data()
    coeff = double_chance_coeff = fora_plus = fora_minus = None
    if data["format"] == "bo2":
        name, coeff, double_chance_coeff = message.text.split("-")
    elif data["format"] == "bo3":
        name, coeff, fora_plus, fora_minus = message.text.split("-")
    else:
        name, coeff = message.text.split("-")
        double_chance_coeff = None

    await state.update_data(
        first_team_name=name,
        first_team_coefficient=coeff,
        first_team_double_chance=double_chance_coeff,
        first_team_fora_plus_coefficient=fora_plus,
        first_team_fora_minus_coefficient=fora_minus,
    )
    result_text = "Введите данные Второй команды:\n"
    if data["format"] == "bo2":
        result_text += "Формат ввода: <b>Название команды-коэффициент победы-коэффициент двойного шанса</b>"
    elif data["format"] == "bo3":
        result_text += "Формат ввода:\n <b>Название команды-коэффициент победы-фора+1.5-фора-1.5</b>"
    else:
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

    data = await state.get_data()
    coeff = double_chance_coeff = fora_plus = fora_minus = None
    if data["format"] == "bo2":
        name, coeff, double_chance_coeff = message.text.split("-")
        double_chance_coeff = float(double_chance_coeff)
    elif data["format"] == "bo3":
        name, coeff, fora_plus, fora_minus = message.text.split("-")
        fora_plus = float(fora_plus)
        fora_plus = float(fora_plus)
    else:
        name, coeff = message.text.split("-")

    coeff = float(coeff)

    await state.update_data(
        second_team_name=name,
        second_team_coefficient=coeff,
        second_team_double_chance=double_chance_coeff,
        second_team_fora_plus_coefficient=fora_plus,
        second_team_fora_minus_coefficient=fora_minus,
    )
    if data["format"] == "bo2":
        result_text = "Введите коэффициент ничьи:\n"
        result_text += "Формат ввода: 1.4"
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=result_text,
        )
        await state.set_state(GameAdd.draw)
    elif data["format"] == "bo3":
        result_text = "Введите коэффициент тотал карт\n"
        result_text += "Формат ввода: тотал 2.5 Б-тотал 2.5 М"
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=result_text,
        )
        await state.set_state(GameAdd.total)
    else:
        result_text = "Введите уровень интересности\n"
        result_text += "Формат ввода: число 1-3"
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=result_text,
        )
        await state.set_state(GameAdd.hype)


@game_add_router.message(GameAdd.total)
async def process_draw_coefficient(message: Message, state: FSMContext) -> None:
    if not validate_total(message.text):
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return

    total_b, total_l = message.text.split("-")
    await state.update_data(
        total_bigger_coefficient=total_b, total_less_coefficient=total_l
    )
    result_text = "Введите уровень интересности\n"
    result_text += "Формат ввода: число 1-3"
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=result_text,
    )
    await state.set_state(GameAdd.hype)


@game_add_router.message(GameAdd.draw)
async def process_draw_coefficient(message: Message, state: FSMContext) -> None:
    if (draw_coefficient := validate_bet_size(message.text)) is None:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат",
        )
        return

    await state.update_data(draw_coefficient=draw_coefficient)
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
