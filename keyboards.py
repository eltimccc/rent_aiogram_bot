from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button_address = KeyboardButton('Адрес')
address = ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True).add(button_address)

conditions = KeyboardButton('Условия')

menu = ReplyKeyboardMarkup(resize_keyboard=True).row(
    button_address, conditions
    ).add(KeyboardButton('Заказать звонок', request_contact=True))

