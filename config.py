import logging
import os

PHOTO_DIR = "cars_photo"
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

TOKEN = '6068983644:AAHL507NB2YFBaKxFfY61ijT3oNHtIJgEds'
MANAGER_ID = 228888741


my_logger = logging.getLogger('my_logger')
my_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
my_logger.addHandler(console_handler)