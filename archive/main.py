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

API_TOKEN = os.environ.get('API_TOKEN') #всё в .env
HOST = os.environ.get('HOST')
DB = os.environ.get('DB')
USER = os.environ.get('USER')
PWD = os.environ.get('PWD')
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


userData = [] #this code is ugly and I have to rewrite it someday... 
page = 0
existingID = 0

def get_keyboard_navigation(big_button, questionid, solutionid): #чувствую, что переход к такой навигации приведёт меня к боли и страданиям
    if big_button == 'open_nav': #кнопки навигации в "открытых вопросах"
        buttons = [
            types.InlineKeyboardButton(text='⬅️', callback_data='open_goback'),
            types.InlineKeyboardButton(text='➡️', callback_data='open_goforward'),
            types.InlineKeyboardButton(text='Ответить', callback_data='open_answer.'+str(questionid))
        ]
    elif big_button == 'active_nav': #кнопки навигации в "активных вопросах" пользователя
        buttons = [
            types.InlineKeyboardButton(text='⬅️', callback_data='active_goback.'+str(questionid)),
            types.InlineKeyboardButton(text='➡️', callback_data='active_goforward.'+str(questionid)),
            types.InlineKeyboardButton(text='Отметить как решение', callback_data=f'active_clthr.{questionid}.{solutionid}')
        ]
    elif big_button == 'closed_nav': #кнопки навигации в "закрытых вопросах"
        buttons = [
            types.InlineKeyboardButton(text='⬅️', callback_data='closed_goback'),
            types.InlineKeyboardButton(text='➡️', callback_data='closed_goforward')
        ]
    else:
        return
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

flag = True
while flag:
    try:
        conn = psycopg2.connect(dbname=DB, user=USER, password=PWD, host=HOST) #указывать в .env
        print('Connection to database is established')
        flag = False
    except Exception as e:
        print("Can't establish connection to database. Error:", e)

greet = 'Привет и добро пожаловать в BonchOverflow! \n\nЗдесь ты можешь задать интересующие тебя вопросы, касающиеся университета и не только. \n\nИспользуя этого бота вы соглашаетесь с правилами эксплуатации BonchOverflow. Ознакомиться с правилами вы можете в пункте "Правила".'

logging.basicConfig(level=logging.INFO)

class AskQuestion(StatesGroup):
    header = State()
    question = State()

class AnswerQuestion(StatesGroup):
    solution = State()

async def get_username(user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = chat.username
        return username
    except Exception as e:
        print("Error while getting username:", e)
        return "404n0tF0uNd"

@dp.message_handler(commands="start")
async def start_greet(message: types.Message, state: FSMContext):
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
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM questions WHERE (userid = {message.from_user.id} AND status = false);")
    questions = cursor.fetchall()
    if len(questions) < 5:
        await AskQuestion.header.set()

        await message.reply("Здесь вы можете задать свой вопрос. Помните, что вопросы, каким-либо образом нарушающие правила проекта, будут удалены! \n\nВведите заголовок вопроса:", reply_markup=keyboard)
    else:
        await message.reply("Достигнут лимит открытых вопросов.")

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

@dp.message_handler(lambda message: len(message.text)>64 or (message.text=='/start'), state=AskQuestion.header)
async def process_header_invalid(message: types.Message):
    if message.text == "/start":
        return await message.reply('Для отмены введения данных нажмите кнопку "Отмена"')
    else:
        return await message.reply("Длина заголовка не должна превышать 64 символа.")

@dp.message_handler(state=AskQuestion.header)
async def process_header(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['header'] = message.text

        await AskQuestion.next()
        await message.reply("Введите текст вопроса:")
    except Exception as e:
        print('Exception found in process_header_invalid:', e)


@dp.message_handler(lambda message: len(message.text)>1250 or (message.text=='/start'), state=AskQuestion.question)
async def process_question_invalid(message: types.Message):
    if message.text == '/start':
        return await message.reply('Для отмены введения данных нажмите кнопку "Отмена"')
    else:
        return await message.reply("Длина вопроса не должна превышать 1250 символов.") #1250*2 = 3500 + 2*ID + Header, лимит = 4096 символа на сообщение в телеграме.

@dp.message_handler(state=AskQuestion.question)
async def process_question(message: types.Message, state: FSMContext):
    global existingID
    try:
        async with state.proxy() as data:
            data['question'] = message.text

        await state.finish()

        userid = message.from_user.id
        username = await get_username(userid)

        cursor = conn.cursor()
        if existingID == 0:
            cursor.execute("INSERT INTO questions(userid, header, question, status, solverid, solution) VALUES ("+str(userid)+", "+"'"+data['header']+"'"+", '"+data['question']+"', false, 0, '') RETURNING id;")
            questionid = cursor.fetchone()[0]
        else:
            questionid = existingID
            cursor.execute(f"UPDATE questions SET header = '{data['header']}' WHERE id = {existingID};")
            cursor.execute(f"UPDATE questions SET question = '{data['question']}' WHERE id = {existingID};")
            existingID = 0
        conn.commit()
        cursor.close()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*['Главное меню']) #на самом деле вопрос отображается не так, исправь
        await message.reply("Ваш вопрос будет отображаться подобным образом: \n\n"
                            f"<b>Вопрос №n, автор: @{username}\nID Вопроса: {questionid}\n\n{data['header']}</b>\n\n{data['question']}", parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
    except Exception as e:
        print('Found exception at process_question:', e)

@dp.message_handler(Text(equals="Активные вопросы"))
async def user_questions(message: types.Message):
    userid = message.from_user.id
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM questions WHERE (userid = {userid} AND status = false);")
    questions = cursor.fetchall()
    cursor.close()
    questions_count = len(questions)
    if questions_count != 0:
        keyboard = types.InlineKeyboardMarkup()
        for i in range(questions_count):
            header = questions[i][2]
            questionid = questions[i][0]
            keyboard.add(types.InlineKeyboardButton(text=header, callback_data = "act."+str(questionid)))
        await message.answer("На данный момент активны следующие вопросы:", reply_markup=keyboard)
    else:
        await message.answer("На данный момент нет активных вопросов.")

@dp.callback_query_handler(Text(startswith="act.")) #act. - активный вопрос (active). Ищем в db questions
async def active_questions_handler(call: types.CallbackQuery):
    call_data = call.data[4::]
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
    keyboard.add(types.InlineKeyboardButton(text="Да", callback_data=f"sol.{call_data}"))
    keyboard.add(types.InlineKeyboardButton(text="Изменить вопрос", callback_data=f"redact.{call_data}"))
    keyboard.add(types.InlineKeyboardButton(text="Закрыть вопрос", callback_data=f"active_clthr.{call_data}.1"))
    await bot.send_message(chat_id=call.from_user.id,text=form_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
    await call.answer()

@dp.callback_query_handler(Text(startswith="redact."))
async def redact_active_handler(call: types.CallbackQuery):
    global existingID

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Отмена'])

    cursor = conn.cursor()
    existingID = int(call.data.split('.')[1])
    cursor.execute(f"SELECT * FROM questions WHERE (id = {existingID} AND status = true);")
    existingRow = cursor.fetchone()
    cursor.close()
    if existingRow == None:
        try:
            await AskQuestion.header.set()

            await bot.send_message(chat_id = call.from_user.id,
                text = "Здесь вы можете изменить свой вопрос. Помните, что вопросы, каким-либо образом нарушающие правила проекта, будут удалены! \n\nВведите заголовок вопроса:",
                reply_markup=keyboard)
        except Exception as e:
            print('Found an exception at redact_active_handler:', e)
    else:
        await bot.send_message(chat_id = call.from_user.id, text = "Вы не можете редактировать закрытые вопросы.")
    await call.answer()

async def update_question_text(message: types.Message, new_text: str, big_button: str, questionid: int, solverid: int):
    await message.edit_text(f"{new_text}", reply_markup=get_keyboard_navigation(big_button, questionid, solverid), parse_mode=types.ParseMode.HTML)

@dp.callback_query_handler(Text(startswith="sol.")) #sol. - ответ (solutions). Ищем в db solutions.
async def active_solutions_handler(call: types.CallbackQuery):
    global userData
    global page
    call_data = call.data[4::]
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM solutions WHERE questionid = {call_data}")
    userData = cursor.fetchall()
    cursor.close()
    if len(userData) == 0:
        await bot.send_message(chat_id=call.from_user.id, text='На данный момент нет ответа на этот вопрос.\n\nВы можете ответить на вопрос самостоятельно через вкладку "Открытые вопросы", а после закрыть его.')
    else:
        page = 0 #начиная с этого момента, Бог отказался от того, чтобы помогать мне в написании этого кода
        row = userData[page]
        username = await get_username(int(row[2]))
        form_text = f"<b>Решение №{page+1}, автор: @@"+username+"</b>\nID Ответа: "+str(row[0])+"\n\n" + str(row[3]) +"\n"
        keyboard = get_keyboard_navigation('active_nav', call_data, row[2])
        await bot.send_message(chat_id=call.from_user.id, text=form_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
    await call.answer()

@dp.callback_query_handler(Text(startswith="active_")) #clthr - закрытый вопрос (Close Thread). Ищем в solutions ответ и автора, в questions вносим автора и меняем на closed.
async def active_nav_handler(call: types.CallbackQuery):
    global userData
    global page
    call_data = call.data.split("_")[1]
    if 'clthr.' in call_data:
        data = call_data[6::].split('.')
        questionid = data[0]
        solverid = data[1]
        cursor = conn.cursor()
        if solverid != '1':
            cursor.execute(f"SELECT * FROM solutions WHERE (questionid = {questionid} AND solverid = {solverid});")
        else:
            cursor.execute(f"SELECT * FROM solutions WHERE id = {solverid};")
            solverid = call.from_user.id
        data = cursor.fetchone()
        solution = data[3] #заменить потом все здесь на нормальные двойные кавычки
        cursor.execute(f"UPDATE questions SET solution = '{solution}' WHERE id = {questionid};")
        cursor.execute(f"UPDATE questions SET solverid = {solverid} WHERE id = {questionid};")
        cursor.execute(f"UPDATE questions SET status = True WHERE id = {questionid};")
        conn.commit()
        cursor.close()
        await bot.send_message(chat_id=call.from_user.id, text="Вопрос закрыт.", parse_mode=types.ParseMode.HTML)

    else:
        action, questionid = call_data.split('.')
        questionid = int(questionid)
        try:
            if action == 'goback':
                page -= 1
                row = userData[page]
                username = await get_username(int(row[2]))
                form_text = f"<b>Решение №{page + 1}, автор: @" + username + "</b>\nID Ответа: " + str(row[0]) + "\n\n" + str(row[3]) + "\n"
                await update_question_text(call.message, form_text, "active_nav", questionid, int(row[2]))

            elif action == 'goforward':
                page += 1
                row = userData[page]
                username = await get_username(int(row[2]))
                form_text = f"<b>Решение №{page + 1}, автор: @" + username + "</b>\nID Ответа: " + str(row[0]) + "\n\n" + str(row[3]) + "\n"
                await update_question_text(call.message, form_text, "active_nav", questionid, int(row[2]))
        except Exception as e: #я не имею ни малейшего понятия, как это дебажить через месяц, но оно выглядит красиво
            print("Found an exception in active questions handler:", e)
    await call.answer()

"""
Блок кода с открытыми вопросами и действиями над ними.
"""

@dp.message_handler(Text(equals="Открытые вопросы"))
async def open_questions(message: types.Message):
    global userData
    global page
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM questions WHERE status = false;")
    userData = cursor.fetchall()
    cursor.close()
    if len(userData) == 0:
        await message.answer(text='На данный момент нет открытых вопросов.')
    else:
        page = 0
        row = userData[page]
        username = await get_username(int(row[1]))
        header = row[2]
        question = row[3]
        questionid = int(row[0])
        form_text = f"<b>Вопрос №{page + 1}, автор: @{username}\nID Вопроса: {questionid}\n\n{header}</b>\n\n{question}"
        keyboard = get_keyboard_navigation('open_nav', questionid, row[page])
        await message.answer(text=form_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)

@dp.callback_query_handler(Text(startswith="open_"))
async def open_questions_handler(call: types.CallbackQuery):
    global userData
    global page

    action = call.data.split("_")[1]
    try:
        if action == "goback":
            if page!=0:
                page -= 1
                row = userData[page]
                username = await get_username(int(row[1]))
                header = row[2]
                question = row[3]
                questionid = int(row[0])
                form_text = f"<b>Вопрос №{page + 1}, автор: @{username}\nID Вопроса: {questionid}\n\n{header}</b>\n\n{question}"
                await update_question_text(call.message, form_text, "open_nav", questionid, int(row[1]))

        elif action == "goforward":
            page += 1
            row = userData[page]
            username = await get_username(int(row[1]))
            header = row[2]
            question = row[3]
            questionid = int(row[0])
            form_text = f"<b>Вопрос №{page + 1}, автор: @{username}\nID Вопроса: {questionid}\n\n{header}</b>\n\n{question}"
            await update_question_text(call.message, form_text, "open_nav", questionid, int(row[1]))

        else:
            questionid = int(action.split('.')[1])
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*['Отмена'])
            userData[0] = questionid

            await AnswerQuestion.solution.set()
            await bot.send_message(chat_id=call.message.chat.id, text="Введите текст ответа:", reply_markup=keyboard)
            await call.answer()
    except Exception as e:
        print('Found an exception in open questions handler:', e)
    await call.answer()

@dp.message_handler(lambda message: len(message.text)>1250 or (message.text=='/start'), state=AnswerQuestion.solution)
async def process_answer_invalid(message: types.Message):
    if message.text == '/start':
        return await message.reply('Для отмены введения данных нажмите кнопку "Отмена"')
    else:
        return await message.reply("Длина ответа не должна превышать 1250 символов.")

@dp.message_handler(state=AnswerQuestion.solution)
async def process_answer(message: types.Message, state: FSMContext):
    global userData

    solution = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["Главное меню", "Открытые вопросы"]
    keyboard.add(*buttons)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM solutions WHERE (questionid = {userData[0]} AND solverid = {message.from_user.id});")
        data = cursor.fetchone()
        if data == None:
            cursor.execute(f"INSERT INTO solutions(questionid, solverid, solution) VALUES ({userData[0]}, {message.from_user.id}, '{solution}');")
        else:
            cursor.execute(f"UPDATE solutions SET solution = '{solution}' WHERE (questionid = {userData[0]} AND solverid = {message.from_user.id});")
        conn.commit()
        cursor.close()
        await state.finish()
        await message.answer(f"Решение внесено.\n\n <b>Текст решения</b>:\n{solution}", parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
    except Exception as e:
        print('Found an exception at process_answer:', e)

"""
Блок кода с закрытыми вопросами и действиями над ними.
"""

@dp.message_handler(Text(equals="Закрытые вопросы"))
async def closed_questions(message: types.Message):
    global userData
    global page

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM questions WHERE status = true;")
    userData = cursor.fetchall()
    cursor.close()
    if len(userData) == 0:
        await message.answer(text='На данный момент нет закрытых вопросов.')
    else:
        page = 0
        row = userData[page]
        asker_username = await get_username(int(row[1]))
        solver_username = await get_username(int(row[5]))
        header = row[2]
        question = row[3]
        solution = row [6]
        questionid = int(row[0])
        form_text = f"<b>Вопрос №{page+1}, автор: @{asker_username}\nID Вопроса: {questionid}\n\n{header}</b>\n\n{question}\n\n" \
                                                                   f"Решение @<b>{solver_username}</b>:\n{solution}"
        keyboard = get_keyboard_navigation('closed_nav', 0, 0)
        await message.answer(text=form_text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)

@dp.callback_query_handler(Text(startswith="closed_"))
async def closed_questions_handler(call: types.CallbackQuery):
    global userData
    global page

    action = call.data.split("_")[1]
    try:
        if action == "goback":
            if page!=0:
                page -= 1
                row = userData[page]
                asker_username = await get_username(int(row[1]))
                solver_username = await get_username(int(row[5]))
                header = row[2]
                question = row[3]
                solution = row[6]
                questionid = int(row[0])
                form_text = f"<b>Вопрос №{page + 1}, автор: @{asker_username}\nID Вопроса: {questionid}\n\n{header}</b>\n\n{question}\n\n" \
                            f"Решение @<b>{solver_username}</b>:\n{solution}"
                await update_question_text(call.message, form_text, "closed_nav", 0, 0)

        elif action == "goforward":
            page += 1
            row = userData[page]
            asker_username = await get_username(int(row[1]))
            solver_username = await get_username(int(row[5]))
            header = row[2]
            question = row[3]
            solution = row[6]
            questionid = int(row[0])
            form_text = f"<b>Вопрос №{page + 1}, автор: @{asker_username}\nID Вопроса: {questionid}\n\n{header}</b>\n\n{question}\n\n" \
                        f"Решение @<b>{solver_username}</b>:\n{solution}"
            await update_question_text(call.message, form_text, "closed_nav", 0, 0)

        else:
            print('ass')
    except Exception as e:
        print('Found an exception in closed questions handler:', e)
    await call.answer()

"""
Прочее
"""

@dp.message_handler(Text(equals="Администрация"))
async def administration(message: types.Message):
    await message.reply(f'Создатель бота: @{await get_username(340772367)}, по вопросам нарушения правил, улучшения бота и самым разнообразным предложениям обращайтесь в телеграм.\n\n Позднее этот раздел будет автоматизирован под систему тикетов.')

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)