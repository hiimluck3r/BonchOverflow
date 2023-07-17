from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import psycopg2
import logging
import os

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
flag = True
while flag:
    try:
        conn = psycopg2.connect(dbname='test_db', user='root', password='root', host='db')
        print('Connection to database is established')
        flag = False
    except Exception as e:
        print("Can't establish connection to database. Error:", e)

greet = 'Привет и добро пожаловать в BonchOverflow! \n\nЗдесь ты можешь задать интересующие тебя вопросы, касающиеся университета и не только. \n\nИспользуя этого бота вы соглашаетесь с правилами эксплуатации BonchOverflow. Ознакомиться с правилами вы можете в пункте "Правила".'

logging.basicConfig(level=logging.INFO)

async def get_username(user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = chat.username
        return username
    except Exception as e:
        print("Error while getting username:", e)
        return "n0tF0U//d"

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
    buttons = ["Администрация"]
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

"""
Блок кода с вопросами пользователя и действиями над ними.
"""

@dp.message_handler(Text(equals="Ваши вопросы"))
async def your_questions(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Задать вопрос", "Активные вопросы"]
    keyboard.add(*buttons)
    buttons = ["Главное меню"]
    keyboard.add(*buttons)
    await message.answer("Здесь вы можете задать вопрос или просмотреть активные на данный момент.\n\n"
                         "Одновременно могут быть активными не более 5 вопросов!", reply_markup=keyboard, parse_mode=types.ParseMode.HTML)

@dp.message_handler(Text(equals="Активные вопросы"))
async def user_questions(message: types.Message):
    userid = message.from_user.id
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions WHERE userid = ' + str(userid) + ' AND status = false;')
    questions = cursor.fetchall()
    cursor.close()
    questions_count = len(questions)
    print(questions)
    if questions_count != 0:
        keyboard = types.InlineKeyboardMarkup()
        for i in range(questions_count):
            header = questions[i][2]
            questionid = questions[i][0]
            print(header, questionid)
            keyboard.add(types.InlineKeyboardButton(text=header, callback_data = "act."+str(questionid)))
        await message.answer("На данный момент активны следующие вопросы:", reply_markup=keyboard)
    else:
        await message.answer("На данный момент нет активных вопросов.")

@dp.callback_query_handler()
async def query_handler(call: types.CallbackQuery):
    if "act." in call.data: #act. - активный вопрос (active). Ищем в db questions
        call_data = call.data[4::]
        print(call_data)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM public.questions WHERE id = '+ call_data+";")
        data = cursor.fetchone()
        cursor.close()
        header = data[2]
        question_text = data[3]
        form_text = "<b>"+str(header)+"</b>\n\n" \
                        "Статус: открыт\n" \
                        "Текст: "+str(question_text)+"\n\n" \
                        "Желаете рассмотреть предложенные ответы?"
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="sol."+call_data))
        await bot.send_message(chat_id=call.from_user.id,text=form_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)

    elif "sol." in call.data: #sol. - ответ (solutions). Ищем в db solutions.
        call_data = call.data[4::]
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM public.solutions WHERE questionid = ' + call_data+";")
        data = cursor.fetchall()
        cursor.close()
        for row in data:
            username = await get_username(int(row[2]))
            form_text = "<b>Решение "+username+"</b>\nID Ответа: "+str(row[0])+"\n\n" + str(row[3]) +"\n"
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Отметить как решение вопроса', callback_data="clthr."+call_data+"."+str(row[2])))
            await bot.send_message(chat_id=call.from_user.id, text=form_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)

    elif "clthr." in call.data: #clthr - закрытый вопрос (Close Thread). Ищем в solutions ответ и автора, в questions вносим автора и меняем на closed.
        data = call.data[6::].split('.')
        questionid = data[0]
        solverid = data[1]
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM public.solutions WHERE questionid = '+questionid+' AND solverid = '+solverid+';')
        data = cursor.fetchone()
        print(data)
        solution = data[3]
        cursor.execute('UPDATE questions SET solution = ' + "'" + solution + "'" + 'WHERE id = '+questionid+';')
        cursor.execute('UPDATE questions SET solverid = '+ solverid + ' WHERE id = '+questionid+';')
        cursor.execute('UPDATE questions SET status = True WHERE id = ' + questionid + ';')
        conn.commit()
        cursor.close()
        await bot.send_message(chat_id=call.from_user.id, text="Вопрос закрыт.", parse_mode=types.ParseMode.HTML)

    else:
        print("Unauthorized data:", call.data) #я обязательно заменю if на match case, наверное.
        pass
"""
Блок кода с открытыми вопросами и действиями над ними.
"""

"""
Блок кода с закрытыми вопросами и действиями над ними.
"""

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)