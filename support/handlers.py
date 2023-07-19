from support.dispatcher import dp, bot
from support import ADMIN
from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

userid = 0

async def get_username(user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = chat.username
        return username
    except Exception as e:
        print("Error while getting username:", e)
        return "404n0tF0uNd"

class sendText(StatesGroup):
    text = State()

@dp.message_handler(commands=['start'])
@dp.message_handler(Text("Вернуться"))
async def greet(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отправить обращение")
    await message.answer("Добро пожаловать в техническую поддержку BonchOverflow!\n\nПожалуйста, укажите в обращении подробную информацию, чтобы мы смогли Вам помочь.", reply_markup=keyboard)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*['Вернуться'])

    current_state = await state.get_state()
    if current_state is None:
        return

    print(f'Cancelling state %r', current_state)
    await state.finish()
    await message.answer('Ввод данных остановлен.', reply_markup=keyboard)

@dp.message_handler(Text("Отправить обращение"))
async def send_ticket(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")

    await sendText.text.set()
    await message.answer("Введите текст обращения:", reply_markup=keyboard)

@dp.callback_query_handler(Text("answer"))
async def send_ticket(call: types.CallbackQuery):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Отмена")

    await sendText.text.set()
    await bot.send_message(chat_id=call.message.chat.id, text="Введите текст обращения:", reply_markup=keyboard)
    await call.answer()

@dp.message_handler(lambda message: len(message.text)>3500 or (message.text=='/start'), state=sendText.text.set())
async def process_text_invalid(message: types.Message):
    if message.text == '/start':
        return await message.answer('Для отмены введения данных нажмите кнопку "Отмена".')
    else:
        return await message.answer("Длина обращения не должна превышать 3500 символов.")

@dp.message_handler(state=sendText.text)
async def process_text(message: types.Message, state: FSMContext):
    global userid

    if int(message.from_user.id) == int(ADMIN):
        await bot.send_message(chat_id=userid, text=f"Ответ тех.поддержки:\n\n{message.text}")
    else:
        userid = message.from_user.id
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Ответить", callback_data="answer"))
        await bot.send_message(chat_id=ADMIN, text=f"Обращение от @{await get_username(message.from_user.id)}, ID: {message.from_user.id}\n\n"
                                                   f"{message.text}", reply_markup=keyboard)
    await state.finish()
    await message.answer("Сообщение отправлено.")

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True
