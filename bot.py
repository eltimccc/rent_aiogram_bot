from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import logging
from aiogram.types import ChatActions
import os
from uuid import uuid4

import keyboards as kb
from config import TOKEN, MANAGER_ID, PHOTO_DIR
from database import Base, CallOrder, session, Car
from datetime import datetime


Base.metadata.create_all(session.get_bind())

bot = Bot(TOKEN)
dp = Dispatcher(bot)


my_logger = logging.getLogger('BOT_LOGGER')
my_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
my_logger.addHandler(console_handler)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """ Обработчик запуска бота. """

    my_logger.info("User %s started the bot.",
                   message.from_user.first_name)
    await message.reply(f"Здравствуйте, {message.from_user.first_name}! Я помогу вам арендовать автомобиль. "
                        "Нажмите на кнопки ниже, чтобы выбрать действие.", reply_markup=kb.menu)


@dp.message_handler(lambda message: message.text == 'Адрес')
async def process_address_command(message: types.Message):
    """ Обработчик кнопки 'Адрес'. """

    my_logger.info("User %s chose the show adress.",
                   message.from_user.first_name)
    map_url = "https://yandex.ru/maps/?um=constructor%3Af85d033fb7a55272dc36551a140bf294f3187a5da834e41040e6b5eecd3b2f19&source=constructor"
    await message.reply("Мы находимся по адресу:\n"
                        "город Псков\nулица Новаторов, дом 2\n"
                        '\n'
                        f"Ссылка на карту: {map_url}")


@dp.message_handler(lambda message: message.text == 'Условия')
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


@dp.message_handler(content_types=['contact'])
async def process_contact(message: types.Message):
    """ Обработчик кнопки 'Заказ звонка'. """

    my_logger.info("User %s chose the order call.",
                   message.from_user.first_name)
    contact = message.contact
    user_name = message.from_user.first_name
    phone_number = contact.phone_number
    await save_call_order(session,
                          user_name=user_name,
                          phone_number=phone_number)
    await bot.send_message(
        chat_id=MANAGER_ID,
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


@dp.message_handler(commands=['create_car'])
async def create_car_handler(message: types.Message):
    """ Создание автомобиля в db """

    my_logger.info("Сar create started.")
    await message.answer('Пожалуйста, загрузите фотографию')

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def save_car_photo(message: types.Message):
    my_logger.info("Сar photo saved.")
    # Получаем объект файла фотографии
    photo = message.photo[-1]
    filename = str(uuid4()) + ".jpg"
    filepath = os.path.join(PHOTO_DIR, filename)
    await photo.download(destination_dir=PHOTO_DIR)
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
    # Обработчик сообщений для заполнения полей автомобиля
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


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    """ /help. """

    await message.reply("Я могу рассказать информацю об огранизации ПрокатПсков!")


@dp.message_handler()
async def echo_message(msg: types.Message):
    """ Эхо. """

    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
