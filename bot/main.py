from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import psycopg2
import logging
import os

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')
HOST = os.environ.get('HOST')
DB = os.environ.get('DB')
USER = os.environ.get('USER')
PWD = os.environ.get('PWD')
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

flag = True
while flag:
    try:
        conn = psycopg2.connect(dbname=DB, user=USER, password=PWD, host=HOST)
        print('Connection to database is established')
        flag = False
    except Exception as e:
        print("Can't establish connection to database. Error:", e)

greet = 'Привет и добро пожаловать в BonchOverflow! \n\nЗдесь ты можешь задать интересующие тебя вопросы, касающиеся университета и не только. \n\nИспользуя этого бота вы соглашаетесь с правилами эксплуатации BonchOverflow. Ознакомиться с правилами вы можете в пункте "Правила".'

logging.basicConfig(level=logging.INFO)

class AskQuestion(StatesGroup):
    header = State()
    question = State()

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

@dp.message_handler(Text(equals="Задать вопрос"))
async def ask_question(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Отмена'])

    await AskQuestion.header.set()

    await message.reply("Здесь вы можете задать свой вопрос. Помните, что вопросы, каким-либо образом нарушающие правила проекта, будут удалены! \n\nВведите заголовок вопроса:", reply_markup=keyboard)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Главное меню'])

    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()

    await message.reply('Ввод данных остановлен. Вернёмся в мёню?', reply_markup=keyboard)

@dp.message_handler(lambda message: len(message.text)>64, state=AskQuestion.header)
async def process_header_invalid(message: types.Message):
    return await message.reply("Длина заголовка не должна превышать 64 символа.")
@dp.message_handler(state=AskQuestion.header)
async def process_header(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['header'] = message.text

    await AskQuestion.next()
    await message.reply("Введите текст вопроса:")

@dp.message_handler(lambda message: len(message.text)>3500, state=AskQuestion.question)
async def process_question_invalid(message: types.Message):
    return await message.reply("Длина вопроса не должна превышать 3500 символов.")

@dp.message_handler(state=AskQuestion.question)
async def process_header(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['question'] = message.text

    await state.finish()

    userid = message.from_user.id
    username = await get_username(userid)

    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions(userid, header, question, status, solverid, solution) VALUES ("+str(userid)+", "+"'"+data['header']+"'"+", '"+data['question']+"', false, 0, '');")
    conn.commit()
    cursor.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Главное меню'])
    await message.reply("Ваш вопрос будет отображаться подобным образом: \n\n"
                        "<b>"+data['header']+"</b>\n"
                                             "Задал: "+username+"\n\n"+data['question'], parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
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
        if len(data) == 0:
            await bot.send_message(chat_id=call.from_user.id, text='На данный момент нет ответа на этот вопрос.\n\nВы можете закрыть вопрос самостоятельно через вкладку "Открытые вопросы".')
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