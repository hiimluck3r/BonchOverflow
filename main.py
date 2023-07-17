from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import json
import logging
import os

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

greet = 'Привет и добро пожаловать в BonchOverflow! \n\nЗдесь ты можешь задать интересующие тебя вопросы, касающиеся университета и не только. \n\nИспользуя этого бота вы соглашаетесь с правилами эксплуатации BonchOverflow. Ознакомиться с правилами вы можете в пункте "Правила".'

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands="start")
async def start_greet(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    goto_menu = types.KeyboardButton(text="Главное меню")
    keyboard.add(goto_menu)
    await message.reply(greet, reply_markup=keyboard)

@dp.message_handler(Text(equals="Главное меню"))
async def menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Правила", "Ваши вопросы"]
    keyboard.add(*buttons)
    buttons = ["Открытые вопросы", "Закрытые вопросы"]
    keyboard.add(*buttons)
    buttons = ["Администрация", "Топ"]
    keyboard.add(*buttons)
    await message.reply("Главное меню", reply_markup=keyboard)

@dp.message_handler(Text(equals="Правила"))
async def rules(message: types.Message):
    ruleString = "<b>Правила</b>\n\n" \
                 "- Пользуясь ботом, вы принимаете на себя добровольное обязательство беспрекословно соблюдать нижеперечисленные правила.\n" \
                 "- Незнание правил не освобождает пользователя от ответственности за их нарушение. Мера наказания в случае нарушения правил выбирается администрацией по усмотрению.\n" \
                 "- Вопросы и ответы не должны нарушать действующее законодательство РФ.\n" \
                 "- Вопросы и ответы не должны содержать непристойные выражения, открытую нецензурную брань, эвфемизмы, оскорбления по какому-либо признаку.\n" \
                 "- Вопросы и ответы не должны содержать политического подтекста.\n" \
                 "- Вопросы и ответы не должны содержать пропаганду оружия, насилия, наркотических или алкогольных веществ, курения и т.п.\n" \
                 "- Вопросы и ответы не должны быть спамом. Реклама без согласия администрации приравнивается к спаму.\n" \
                 "- Запрещено целенаправленное размещение ложной информации.\n"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Главное меню"]
    keyboard.add(*buttons)
    await message.answer(ruleString, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)

@dp.message_handler(Text(equals="Ваши вопросы"))
async def your_questions(message: types.Message):


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)