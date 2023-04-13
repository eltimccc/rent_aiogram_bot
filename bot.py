from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import logging
from aiogram.types import ChatActions
import os
from uuid import uuid4
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import keyboards as kb
from config import TOKEN, MANAGER_ID, PHOTO_DIR
from database import Base, CallOrder, session, Car
from datetime import datetime


Base.metadata.create_all(session.get_bind())

bot = Bot(TOKEN)
dp = Dispatcher(bot)


my_logger = logging.getLogger('BOT_LOGGER')
my_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
file_handler = logging.FileHandler('bot_logs.txt')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
my_logger.addHandler(console_handler)
my_logger.addHandler(file_handler)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """ Обработчик запуска бота. """
    my_logger.info("User %s started the bot.", message.from_user.first_name)

    with open(f"{PHOTO_DIR}/logo.jpg", "rb") as photo_file:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_file,
            caption=f"""Здравствуйте, {message.from_user.first_name}!
Я помогу вам арендовать автомобиль.
Воспользуйтесь меню, чтобы выбрать действие.""")


@dp.message_handler(commands=['adds'])
async def process_address_command(message: types.Message):
    """ Обработчик кнопки 'Адрес'. """

    my_logger.info("User %s chose the show adress.",
                   message.from_user.first_name)
    map_url = "https://clck.ru/3484XH"
    await message.reply("Мы находимся по адресу:\n"
                        "город Псков\nулица Новаторов, дом 2\n"
                        '\n'
                        f"Ссылка: {map_url}")


@dp.message_handler(commands=['rules'])
async def get_conditions(message: types.Message):
    """ Обработчик кнопки 'Условия'. """

    my_logger.info("User %s chose the rental conditions.",
                   message.from_user.first_name)

    await message.reply(
        "Вот наши условия для взятия автомобиля в прокат:\n"
        "1. Возраст - от 23-х лет;\n"
        "2. Наличие водительского удостоверения категории B\n"
        'со стажем от 3-х лет;\n'
        "3. Залог за автомобиль - 6000 рублей;\n"
        "4. Аренда возможна только на территории Российской Федерации.",
    )


@dp.message_handler(commands=['callback'])
async def process_callback_command(message: types.Message):
    """ Обработчик команды '/callback'. """
    my_logger.info("User %s chose the order call.",
                   message.from_user.first_name)
    reply_markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    button_contact = types.KeyboardButton(
        'Отправить контакт', request_contact=True)
    reply_markup.add(button_contact)
    await bot.send_message(chat_id=message.chat.id,
                           text='Для заказа звонка, пожалуйста, отправьте Ваш контакт.',
                           reply_markup=reply_markup)


@dp.message_handler(content_types=['contact'])
async def process_contact(message: types.Message):
    """ Обработчик отправки контакта пользователем. """
    my_logger.info("User %s sent contact.", message.from_user.first_name)
    contact = message.contact
    user_name = message.from_user.first_name
    phone_number = contact.phone_number
    await save_call_order(session,
                          user_name=user_name,
                          phone_number=phone_number)
    await bot.send_message(chat_id=message.chat.id,
                           text='Мы Вам перезвоним в ближайшее время!')
    await bot.send_message(chat_id=MANAGER_ID,
                           text=f"Потенциальный клиент {user_name} "
                                f"просит перезвонить по номеру телефона {phone_number}")


async def save_call_order(session, user_name: str, phone_number: str):
    """ Сохранение потенциального клиента в db """
    my_logger.info("User %s insert order call to database.",
                   user_name)

    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    call_order = CallOrder(user_name=user_name,
                           phone_number=phone_number,
                           date=date)
    session.add(call_order)
    session.flush()
    session.commit()
    session.close()


@dp.message_handler(commands=['cars'])
async def show_cars(message: types.Message):
    """Показать список марок автомобилей."""
    my_logger.info("User %s chose the show all cars.",
                   message.from_user.first_name)
    cars = session.query(Car).all()
    car_brands = [car.car_brand for car in cars]

    keyboard = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text=brand,
                                          callback_data=brand)
               for brand in car_brands]
    keyboard.add(*buttons)

    text = "Выберите марку автомобиля:"
    await bot.send_message(chat_id=message.chat.id,
                           text=text,
                           reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data)
async def process_callback_button(callback_query: types.CallbackQuery):
    """Обработчик кнопок выбора марки автомобиля."""

    car_brand = callback_query.data
    car = session.query(Car).filter_by(car_brand=car_brand).first()

    if car:
        with open(os.path.join(PHOTO_DIR, car.photo), 'rb') as photo_file:
            await bot.send_photo(chat_id=callback_query.message.chat.id,
                                 photo=photo_file,
                                 caption=f"Марка: {car.car_brand}\nГод выпуска: {car.year}\nКоробка передач: {car.transmission}\nКондиционер: {car.air_cold}")
    else:
        text = "К сожалению, информация об этом автомобиле отсутствует в нашей базе данных."
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=text)

    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['create_car'])
async def create_car_handler(message: types.Message):
    """ Создание автомобиля в db """

    my_logger.info("Сar create started.")
    await message.answer('Пожалуйста, загрузите фотографию')


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def save_car_photo(message: types.Message):
    my_logger.info("Сar photo saved.")
    photo = message.photo[-1]
    filename = f"file_{str(uuid4())}.jpg"
    filepath = os.path.join(PHOTO_DIR, filename)
    await photo.download(destination=filepath)
    car = Car(photo=filename)

    session.add(car)
    session.commit()

    await message.answer('Фотография сохранена')
    await ask_car_brand(message.from_user.id)


async def ask_car_brand(user_id):
    await bot.send_message(user_id, "Введите марку автомобиля:")


async def ask_year(user_id, car_brand):
    await bot.send_message(user_id, f"Введите год выпуска для автомобиля {car_brand}:")


async def ask_transmission(user_id, car_brand, year):
    await bot.send_message(user_id, f"Введите тип коробки передач для автомобиля {car_brand} {year} года выпуска:")


async def ask_air_cold(user_id, car_brand, year, transmission):
    await bot.send_message(user_id, f"Введите наличие кондиционера для автомобиля {car_brand} {year} года выпуска, тип коробки передач: {transmission}:")


@dp.message_handler()
async def process_car_info(message: types.Message):
    user_id = message.from_user.id
    car = session.query(Car).order_by(Car.id.desc()).first()

    if not car.car_brand:
        car.car_brand = message.text
        session.commit()
        await ask_year(user_id, car.car_brand)

    elif not car.year:
        try:
            year = int(message.text)
            car.year = year
            session.commit()
            await ask_transmission(user_id, car.car_brand, year)
        except ValueError:
            await bot.send_message(user_id, "Введите год в виде числа, например: 2022")

    elif not car.transmission:
        car.transmission = message.text
        session.commit()
        await ask_air_cold(user_id, car.car_brand, car.year, car.transmission)

    elif not car.air_cold:
        car.air_cold = message.text
        session.commit()
        await bot.send_message(user_id, "Данные сохранены")


if __name__ == '__main__':
    executor.start_polling(dp)
