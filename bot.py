from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import keyboards as kb
from config import TOKEN, MANAGER_ID
from database import Base, CallOrder, session

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
async def process_hi5_command(message: types.Message):
    my_logger.info("User %s started the bot.", message.from_user.first_name)
    await message.reply(f"Здравствуйте, {message.from_user.first_name}! Я помогу вам арендовать автомобиль. "
                        "Нажмите на кнопки ниже, чтобы выбрать действие.", reply_markup=kb.menu)


@dp.message_handler(lambda message: message.text == 'Адрес')
async def process_address_command(message: types.Message):
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
    my_logger.info("User %s chose the order call.", message.from_user.first_name)
    contact = message.contact
    user_name = message.from_user.first_name
    phone_number = contact.phone_number
    await save_call_order(session, user_name=user_name, phone_number=phone_number)
    await bot.send_message(
        chat_id=MANAGER_ID,
        text=f"Потенциальный клиент {user_name} "
        f"просит перезвонить по номеру телефона {phone_number}")


async def save_call_order(session, user_name: str, phone_number: str):
    call_order = CallOrder(user_name=user_name, phone_number=phone_number)
    session.add(call_order)
    session.flush()
    session.commit()
    session.close()


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Я могу рассказать информацю об огранизации ПрокатПсков!")


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
