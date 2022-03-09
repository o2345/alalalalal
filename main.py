import vkbot
import config
import json
from datetime import datetime
import requests
from asset import text as mess
import random
from db import *
from asset import keyboard
import time
from classes.tictacgame import TicTacGame



class Bot:
    def __init__(self, token):
        con()
        self.bot = vkbot.VkBot(token=token)
        self.startime = datetime.now()
        self.user = []
        self.send = self.bot.send_message
        if os.path.exists('asset/stat.txt'):
            pass
        else:
            file = open('asset/stat.txt', 'w')
            file.write(mess.writeFile)
            file.close()
            print('Создал файл stat.txt')
        print(f'Успешный запуск бота @{self.bot.get_me().username}')

        @self.bot.message_handler(commands=['start'])
        def startCommand(message):
            text = message.text.split(' ')
            user_id = message.from_user.id
            infoUser = Global.select().where(Global.user_id == user_id)
            if infoUser.exists():
                if self.send(message.from_user.id, 'Для управления ботом воспользуйтесь кнопками',
                              reply_markup=keyboard.menuUser)
            else:
                Global.create(
                    user_id=user_id,
                    username='@' + str(message.from_user.username)
                )


        @self.bot.message_handler(content_types=['text'])
        def userCommand(message):
            TicTac = TicTacGame(self.bot)
            chat_id = message.chat.id
            user_id = message.from_user.id
            userInfo = Global.select().where(Global.user_id == user_id)
            print(f'Ввел команду: {message.text} | {user_id}')
            if userInfo.exists():
                Global.update(username='@' + str(message.from_user.username)).where(
                    Global.user_id == message.from_user.id).execute()
                
                if message.text == '🌪Игры':
                    self.send(user_id, 'Выберите во что хотите сыграть', reply_markup=keyboard.menuGame)
                elif message.text == '✅Крестики, Нолики':
                    with open(f'photo/CrestGame.jpg', 'rb') as f1:
                        self.bot.send_photo(chat_id=message.from_user.id, reply_markup=TicTac.allGame(), photo=f1)
                        f1.close()

            else:
                self.send(chat_id, 'Введите команду start')

       
        @self.bot.callback_query_handler(func=lambda c: True)
        def inline(c):
            TicTac = TicTacGame(self.bot)
            userCmd = usersCommandHandler(self.bot)
            Global.update(username='@' + str(c.from_user.username)).where(Global.user_id == c.from_user.id).execute()
            user_id = c.from_user.id
            infoUser = Global.select().where(Global.user_id == c.from_user.id)
            print(f'Нажал кнопку {c.data} | {user_id}')
            self.bot.clear_step_handler_by_chat_id(chat_id=user_id)
            if infoUser.exists():
                if c.data == 'createGame':
                    self.bot.register_next_step_handler(userCmd.gameCreate)
                elif c.data == 'myGame':
                    try:
                        self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                        self.send(
                            reply_markup=keyboard.gameUser(user_id))
                    
               
            else:
                self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                self.send(user_id, 'Введите команду /start')
