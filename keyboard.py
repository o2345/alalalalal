from telebot import types
from db import *
from config import *

createGame = types.InlineKeyboardButton(text='🔥Создать игру', callback_data='createGame')

menuUser = types.ReplyKeyboardMarkup(True, False)
menuUser.add('⚠Помощь⚠')

menuGame = types.ReplyKeyboardMarkup(True, False)
menuGame.add('✅Крестики, Нолики')
reloadKey = types.InlineKeyboardMarkup()

def informKeyboard():
    markup = types.InlineKeyboardMarkup()
    help = types.InlineKeyboardButton(text='✅Поддержка', url=f't.me/{linkTg[1:]}')
    rulesGame = types.InlineKeyboardButton(text='📕Правила игры,')
    markup.add(rulesGame)
    return markup