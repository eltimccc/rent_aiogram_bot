import logging
import os

PHOTO_DIR = "cars_photo"
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)


my_logger = logging.getLogger('BOT_LOGGER')
my_logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
file_handler = logging.FileHandler('bot_logs.txt')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
my_logger.addHandler(console_handler)
my_logger.addHandler(file_handler)