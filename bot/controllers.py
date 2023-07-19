from aiogram import types
from bot.dispatcher import bot

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

async def get_username(user_id):
    try:
        chat = await bot.get_chat(user_id)
        username = chat.username
        return username
    except Exception as e:
        print("Error while getting username:", e)
        return "404n0tF0uNd"