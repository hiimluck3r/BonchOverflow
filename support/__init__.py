import os
from dotenv import load_dotenv

load_dotenv()

SUPPORT_TOKEN = os.getenv('SUPPORT_TOKEN') #всё в .env
ADMIN = os.getenv('ADMIN')