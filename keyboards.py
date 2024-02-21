from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks import CancelCallback, GameCallback


def base_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Назад", callback_data=CancelCallback())

    return builder.as_markup()


def home_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Матчи", callback_data=GameCallback())

    # builder.attach(base_keyboard())
    # builder.adjust(3, 1)

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
