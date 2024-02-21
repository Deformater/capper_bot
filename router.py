import datetime

from aiogram import Router, html, F
from aiogram.filters import CommandStart, Command, CommandObject, ExceptionTypeFilter
from aiogram.types import (
    Message,
    InlineQuery,
    CallbackQuery,
    ReplyKeyboardRemove,
    ErrorEvent,
    ChatMemberLeft
)
    
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from keyboards import base_keyboard, home_keyboard
from callbacks import CancelCallback, GameCallback
from data.models import Game, User


import settings


dlg_router = Router()


class Form(StatesGroup):
    name = State()
    laba = State()
    stream = State()
    date = State()
    action = State()


# @dlg_router.error(ExceptionTypeFilter(KeyError), F.update.query.as_("query"))
# async def error_handler(event: ErrorEvent, query: CallbackQuery) -> None:
#         await query.message.answer("Что-то пошло не так, перезапустите бота /start")


@dlg_router.message(CommandStart())
async def command_start(message: Message) -> None:

    user = await User.get_or_create(tg_id=message.chat.id)
    user_channel_status = await message.bot.get_chat_member(chat_id=settings.GROUP_NAME, user_id=message.chat.id)
    
    if user_channel_status.status == 'left':
        await message.answer(
            f"Вы не подписаны на группу {settings.GROUP_NAME}",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            f"Вы подписаны на {settings.GROUP_NAME}",
            reply_markup=home_keyboard(),
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


# @dlg_router.message(Form.name)
# async def process_name(message: Message, state: FSMContext) -> None:
#     if name_validation(message.text):
#         await state.update_data(name=message.text.split())
#         await state.set_state(Form.laba)
#         await message.answer("Выберите предмет", reply_markup=laba_keyboard())
#     else:
#         await message.answer("Неверный формат ввода")


# Лаба колбек
@dlg_router.callback_query(GameCallback.filter())
async def laba_handler(
    query: CallbackQuery, callback_data: GameCallback
) -> None:
    games = await Game.all()
    today_games = []
    for game in games:
        print(game.game_starts_at.date(), datetime.date.today())
        if game.game_starts_at.date() == datetime.date.today():
            print(game)
            today_games.append(f"{game.first_team_name} vs {game.second_team_name} {game.format}")
    
    result_text = "\n".join(today_games)
    if today_games:
        await query.message.edit_text(
            text=f'{result_text}', reply_markup=base_keyboard()
        )
    else:
        await query.message.edit_text(
            text=f"Сегодня нет игр(", reply_markup=base_keyboard()
        )


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

