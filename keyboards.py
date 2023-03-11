from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button_address = KeyboardButton('Адрес')
address = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True).add(button_address)

conditions = KeyboardButton('Условия')
cars = KeyboardButton('Автомобили')

menu = ReplyKeyboardMarkup(resize_keyboard=True).row(
    button_address,
    conditions,
    cars
).add(KeyboardButton('Заказать звонок', request_contact=True))

create_car = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Автомобили", callback_data="show_cars"),
        ]
    ]
)