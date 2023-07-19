import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN') #всё в .env
HOST = os.getenv('HOST')
DB = os.getenv('DB')
USER = os.getenv('USER')
PWD = os.getenv('PWD')