# -*- coding: utf-8 -*-

import telebot
import config
import json
import math
import os.path
import psutil as ps
from datetime import datetime
import requests
from asset import text as mess
import random
from threading import Thread
from db import *
from asset import keyboard
from config import linkTg
from classes.usersCommand import usersCommandHandler
import time
from asset import func
from classes.tictacgame import TicTacGame
from classes.adminCommand import adminCommandHandler


class Bot:
    def __init__(self, phone, token, admin_id, qiwiApi):
        con()
        self.bot = telebot.TeleBot(token=token, threaded=True, parse_mode='HTML')
        self.phone = phone
        self.qiwiApi = qiwiApi
        self.startime = datetime.now()
        self.user = []
        self.send = self.bot.send_message
        self.admin_id = admin_id
        self.listCheck = []
        self.userDay = []
        self.give24give = []
        self.give24pay = []
        Thread(target=self.zeroListCheck).start()
        print('Запущен поток 1')
        Thread(target=self.clearUserHours).start()
        print('Запущен поток 2')
        Thread(target=self.clearUserDay).start()
        print('Запущен поток 3')
        Thread(target=self.clear24give).start()
        print('Запущен поток 4')
        Thread(target=self.clear24pay).start()
        print('Запущен поток 5')
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
                if len(text) == 2:
                    if Global.select().where(Global.user_id == text[1]).exists():
                        if infoUser[0].referal == 0:
                            if user_id != int(text[1]):
                                Global.update(referal=text[1]).where(Global.user_id == message.from_user.id).execute()
                                Global.update(referalCount=Global.referalCount + 1).where(
                                    Global.user_id == text[1]).execute()
                                self.send(message.from_user.id, 'Реферальный код активирован',
                                          reply_markup=keyboard.menuUser)
                        else:
                            self.send(message.from_user.id, 'Вы уже являетесь рефералом',
                                      reply_markup=keyboard.menuUser)
                    else:
                        self.send(message.from_user.id, 'Пользователя не существует', reply_markup=keyboard.menuUser)
                else:
                    self.send(message.from_user.id, 'Для управления ботом воспользуйтесь кнопками',
                              reply_markup=keyboard.menuUser)
            else:
                Global.create(
                    user_id=user_id,
                    username='@' + str(message.from_user.username)
                )
                self.user.append(user_id)
                if len(text) == 2:
                    if Global.select().where(Global.user_id == user_id).exists():
                        if user_id != int(text[1]):
                            Global.update(referalCount=Global.referalCount + 1).where(
                                Global.user_id == text[1]).execute()
                            Global.update(referal=text[1]).where(Global.user_id == message.from_user.id).execute()
                            self.send(message.from_user.id, mess.start, reply_markup=keyboard.menuUser)
                    else:
                        self.send(message.from_user.id, mess.start, reply_markup=keyboard.menuUser)
                else:
                    self.send(message.from_user.id, mess.start, reply_markup=keyboard.menuUser)

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
                if message.text == '😎21 Очко':
                    with open(f'photo/gamelist.jpg', 'rb') as f1:
                        self.bot.send_photo(chat_id=chat_id, caption='♻Доступные игры: ', photo=f1,
                                            reply_markup=keyboard.gameAll())
                        f1.close()
                elif message.text == '🌪Игры':
                    self.send(user_id, 'Выберите во что хотите сыграть', reply_markup=keyboard.menuGame)
                elif message.text == '🖥 Кабинет':
                    with open(f'photo/cabinet.jpg', 'rb') as f1:
                        self.bot.send_photo(chat_id=chat_id,
                                            caption=mess.profile.format(user_id, userInfo[0].balance,
                                                                        userInfo[0].countWin + userInfo[0].countBad,
                                                                        userInfo[0].countWin, userInfo[0].countBad),
                                            reply_markup=keyboard.cabinet, photo=f1)
                        f1.close()
                elif message.text == '📜 Информация':
                    with open(f'photo/cabinet.jpg', 'rb') as f1:
                        game, balance = func.statBase()
                        self.bot.send_photo(chat_id=chat_id,
                                            caption=f'На данный момент пользователи сыграли {game} игр на сумму {balance} рублей.',
                                            reply_markup=keyboard.informKeyboard(), photo=f1)
                        f1.close()
                elif message.text == '⚠Помощь⚠':
                    self.send(text=f'😎Бота разработал: @gop_len\n🚨Поддержка: {linkTg}', chat_id=chat_id)
                elif message.text == '/admin':
                    if message.from_user.id == self.admin_id:
                        self.send(user_id, 'Вам открылся доступ в админку',
                                  reply_markup=keyboard.adminPanel)
                    elif userInfo[0].adm:
                        self.send(user_id, 'Вам открылся доступ в админку',
                                  reply_markup=keyboard.adminPanel)
                elif message.text == '✅Крестики, Нолики':
                    with open(f'photo/CrestGame.jpg', 'rb') as f1:
                        self.bot.send_photo(chat_id=message.from_user.id, caption='📛Доступные игры📛', reply_markup=TicTac.allGame(), photo=f1)
                        f1.close()
                elif message.text == '🔥Вернуться назад🔥':
                    self.send(message.from_user.id, 'Вы успешно вернулись назад', reply_markup=keyboard.menuUser)
                else:
                    if user_id == self.admin_id:
                        adminCommand(message)
                    elif userInfo[0].adm:
                        adminCommand(message)
            else:
                self.send(chat_id, 'Введите команду /start')

        def adminCommand(message):
            reload = adminCommandHandler(self.bot)
            chat_id = message.from_user.id
            if message.text == 'Выдать баланс':
                addBalance = self.send(chat_id, '[✅]Введите id пользователя: ', reply_markup=keyboard.cancelButton)
                self.bot.register_next_step_handler(addBalance, reload.giveBalanceFirst)
            elif message.text == 'Выдать админа':
                admin = self.send(chat_id, 'Введите id пользователя: ')
                self.bot.register_next_step_handler(admin, reload.giveAdmin)
            elif message.text == 'Забрать баланс':
                delBalance = self.send(chat_id, '[✅]Введите id пользователя: ', reply_markup=keyboard.cancelButton)
                self.bot.register_next_step_handler(delBalance, reload.delBalanceFirst)
            elif message.text == 'Управление пользователями':
                self.send(chat_id, '[✅]Выберите действие', reply_markup=keyboard.usersAdm)
            elif message.text == 'Информация по боту':
                self.send(chat_id, '[✅]Выберите действие', reply_markup=keyboard.informAdmin)
            elif message.text == '<<<Назад':
                self.send(message.from_user.id, 'Вам открылся доступ в админку',
                          reply_markup=keyboard.adminPanel)
            elif message.text == 'Назад':
                self.send(message.from_user.id, 'Вы вошли в меню пользователя', reply_markup=keyboard.menuUser)
            elif message.text == 'Сервер':
                self.send(chat_id, self.serverInform())
            elif message.text == 'Статистика':
                self.send(message.from_user.id, self.statsInform())
            elif message.text == 'Реф.процент':
                self.send(message.from_user.id, func.persentRef())
            elif message.text == 'Изменить реф.процент':
                persNew = self.send(message.from_user.id, 'Введите реферальный %: ')
                self.bot.register_next_step_handler(persNew, reload.refPersNew)
            elif message.text == 'Рассылка':
                category = self.send(chat_id, 'Введите текст рассылка', reply_markup=keyboard.cancelButton)
                self.bot.register_next_step_handler(category, reload.rassulkaStart)
            elif message.text == 'Ком.процент':
                self.send(message.from_user.id, func.persentGive())
            elif message.text == 'Изменить ком.процент':
                persNew = self.send(message.from_user.id, 'Введите коммисионный %: ')
                self.bot.register_next_step_handler(persNew, reload.refComNew)
            elif message.text == 'Поставить реф.процент':
                user_id = self.send(message.from_user.id, 'Введите id пользователя: ')
                self.bot.register_next_step_handler(user_id, reload.referalPersentOne)
            elif message.text == 'Удалить игру':
                self.send(chat_id, 'Выберите игру для удаления', reply_markup=keyboard.gameAdminDelete())
            elif message.text == 'Управление промо':
                self.send(chat_id, 'Выберите действие', reply_markup=keyboard.promoRemoute())
            elif message.text == 'Управление Qiwi':
                self.send(chat_id, 'Вам открылся раздел "Управление Qiwi"', reply_markup=keyboard.qiwiAdm)
            elif message.text == 'Баланс Qiwi':
                self.send(chat_id, f'Баланс вашего кошелька: {reload.balanceQiwi()}р')
            elif message.text == 'Информация на пользователя':
                idUser = self.send(chat_id, 'Введите (id/username) пользователя: ')
                self.bot.register_next_step_handler(idUser, reload.informUsers)
            elif message.text == 'Вывести деньги':
                qiwi = self.send(chat_id, 'Введите киви кошелек: ')
                self.bot.register_next_step_handler(qiwi, reload.sendQiwiAdmFirst)

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
                    balance = self.send(user_id, 'Введите ставку: ')
                    self.bot.register_next_step_handler(balance, userCmd.gameCreate)
                elif c.data == 'myGame':
                    try:
                        self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                        self.send(
                            chat_id=user_id, text='♻Ваши игры: ',
                            reply_markup=keyboard.gameUser(user_id))
                    except:
                        pass
                elif c.data == 'back':
                    try:
                        self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                        self.send(
                                    chat_id=user_id,
                                    text='♻Доступные игры: ',
                                    reply_markup=keyboard.gameAll())
                    except:
                        pass
                elif c.data == 'reloadGame':
                    try:
                        self.bot.delete_message(user_id, c.message.message_id)
                        self.send(user_id, '♻Доступные игры: ', reply_markup=keyboard.gameAll())
                    except:
                        pass
                elif 'gameCon_' in c.data:
                    idGame = c.data[8:]
                    infoGame = Games.select().where(Games.id == idGame)
                    if not infoGame.exists:
                        if infoGame[0].gamerTwo == 0:
                            self.send(user_id, 'Игры не сущеcтвует', reply_markup=keyboard.reloadGame)
                    else:
                        userCmd.connectGame(user_id, idGame)
                elif 'firstAdd_' in c.data:
                    idGame = c.data[9:]
                    userCmd.firstAddCard(idGame, user_id, c)
                elif 'firstGive_' in c.data:
                    idGame = c.data[10:]
                    userCmd.firstGive(idGame, user_id, c)
                elif 'twoAdd_' in c.data:
                    idGame = c.data[7:]
                    userCmd.twoAddCard(idGame, user_id, c)
                elif 'allIn_' in c.data:
                    idGame = c.data[6:]
                    userCmd.allIn(idGame, user_id, c)
                elif 'gameDel_' in c.data:
                    idGame = c.data[8:]
                    userCmd.dellGame(idGame, user_id, c)
                elif c.data == 'refSys':
                    if infoUser[0].referalPersonal == 0:
                        self.send(user_id,
                                  mess.refSystem.format(func.persentRef(), self.bot.get_me().username, user_id,
                                                        infoUser[0].referalCount))
                    else:
                        self.send(user_id,
                                  mess.refSystem.format(infoUser[0].referalPersonal, self.bot.get_me().username,
                                                        user_id,
                                                        infoUser[0].referalCount))
                elif c.data == 'addBalanceQiwi':
                    userHistory = payBalance.select().where(payBalance.user_id == user_id)
                    comments = random.randint(999999, 9999999)
                    if userHistory.exists():
                        if not userHistory[0].status:
                            self.send(user_id,
                                      mess.textPay.replace('{com}', str(userHistory[0].comment)).replace('{num}',
                                                                                                         str(
                                                                                                             self.phone)).replace(
                                          '{link}', linkTg), reply_markup=keyboard.linkPay(userHistory[0].comment))
                        else:
                            payBalance.update(comment=comments, status=False).where(
                                payBalance.user_id == user_id).execute()
                            self.send(user_id,
                                      mess.textPay.replace('{com}', str(comments)).replace('{num}',
                                                                                           str(self.phone)).replace(
                                          '{link}', linkTg), reply_markup=keyboard.linkPay(comments))
                    else:
                        payBalance.create(
                            user_id=user_id,
                            comment=comments)
                        self.send(user_id,
                                  mess.textPay.replace('{com}', str(comments)).replace('{num}',
                                                                                       str(self.phone)).replace(
                                      '{link}', linkTg), reply_markup=keyboard.linkPay(comments))
                elif c.data == 'addBalance':
                    try:
                        self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                        self.send(user_id, 'Выберите платежную систему', reply_markup=keyboard.payment())
                    except:
                        pass
                elif c.data == 'addBalanceBtc':
                    self.send(user_id, f'Чеки отправлять: {config.linkTg}')
                elif c.data == 'checkPay':
                    userPay = payBalance.select().where(payBalance.user_id == c.from_user.id,
                                                        payBalance.status == False)
                    if c.from_user.id not in self.listCheck:
                        self.listCheck.append(c.from_user.id)
                        if userPay.exists():
                            Thread(target=self.check_pay, args=(userPay[0].comment, c.from_user.id, c)).start()
                        else:
                            self.send(c.from_user.id, '[❌]Вначале выполните команду <pre>💰Пополнить баланс</pre>')
                    else:
                        self.send(c.from_user.id, '[❌]Подождите прежде чем проверять')
                elif c.data == 'giveMoney':
                    numberUser = self.send(user_id, '📤 Введите ваш Qiwi Кошелек (Без +):')
                    self.bot.register_next_step_handler(numberUser, self.sendQiwi)
                elif c.data == 'top10':
                    try:
                        self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                        self.send(chat_id=user_id, text='ℹИмя |🕹 Игры |🏆 Победы |☹️ Проигрыши',
                                  reply_markup=keyboard.top10gamers())
                    except:
                        pass
                elif c.data == 'back2':
                    game, balance = func.statBase()
                    try:
                        self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                        self.send(user_id, f'На данный момент пользователи сыграли {game} игр на сумму {balance} рублей.',
                                  reply_markup=keyboard.informKeyboard())
                    except:
                        pass
                elif c.data == 'promoActivate':
                    promo = self.send(user_id, 'Введите промо-код: ')
                    self.bot.register_next_step_handler(promo, userCmd.promoActivate)
                elif c.data == 'createTicTac':
                    balanceGame = self.send(user_id, 'Введите ставку:')
                    self.bot.register_next_step_handler(balanceGame, TicTac.createGame, c.from_user.id)
                    TicTac.createGame(c.from_user.id)
                elif c.data == 'reloadTicTac':
                    self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                    self.send(user_id, 'Выберите игру', reply_markup=TicTac.allGame())
                if c.data[:5] == 'bomb_':
                    params = c.data[5:].split(':')
                    if params[0].isdigit():
                        infoGame = GamesTicTac.select().where(GamesTicTac.idGame == params[1],
                                                              GamesTicTac.status == False)
                        if infoGame[0].creater == c.from_user.id:
                            try:
                                self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                            except:
                                pass
                            TicTac.tic(params[1], params[0], c)
                        elif infoGame[0].gamerTwo == c.from_user.id:
                            try:
                                self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                            except:
                                pass
                            TicTac.tac(params[1], params[0], c)
                        else:
                            self.send(user_id, 'Сейчас не ваш ход!')
                    else:
                        self.send(c.from_user.id, 'Клетка занята')
                elif c.data[:11] == 'connectTic_':
                    idGame = c.data[11:]
                    TicTac.connectTicTac(idGames=idGame, user_id=c.from_user.id)
                else:
                    if user_id == self.admin_id:
                        adminInline(c)
                    elif infoUser[0].adm:
                        adminInline(c)
            else:
                self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                self.send(user_id, 'Введите команду /start')

        def adminInline(c):
            reload = adminCommandHandler(self.bot)
            user_id = c.from_user.id
            if c.data == 'closeMessage':
                try:
                    self.bot.delete_message(chat_id=user_id, message_id=c.message.message_id)
                except:
                    pass

            elif 'send_' in c.data:
                perm = c.data[5:]
                ready = perm.split(':')
                reload.sendMoney(ready, c)

            elif 'backMoney_' in c.data:
                perm = c.data[10:]
                ready = perm.split(':')
                reload.backMoney(ready, c)

            elif 'gameDelAdmin_' in c.data:
                idGame = c.data[13:]
                reload.deleteGameAdmin(idGame, user_id)

            elif c.data == 'createPromo':
                promo = self.send(user_id, 'Введите название промо-кода: ')
                self.bot.register_next_step_handler(promo, reload.promoCreateFirst)

            elif c.data == 'deletePromo':
                promo = self.send(user_id, 'Введите название промо-кода: ')
                self.bot.register_next_step_handler(promo, reload.deletePromo)

            elif c.data == 'activePromo':
                Thread(target=reload.activePromoNow, args=(c.data, c)).start()

        self.bot.infinity_polling(True)

    def clearUserHours(self):
        while True:
            time.sleep(3600)
            self.user.clear()

    def clearUserDay(self):
        while True:
            time.sleep(86400)
            self.userDay.clear()

    def zeroListCheck(self):
        while True:
            time.sleep(60)
            self.listCheck.clear()

    def clear24pay(self):
        while True:
            time.sleep(86400)
            self.give24pay.clear()

    def clear24give(self):
        while True:
            time.sleep(86400)
            self.give24give.clear()

    @func.error_decorator
    def check_pay(self, comment, user_id, data):
        userInfo = Global.select().where(Global.user_id == user_id)
        try:
            h = requests.get(
                'https://edge.qiwi.com/payment-history/v1/persons/' + str(self.phone) + '/payments?rows=50',
                headers={'Accept': 'application/json',
                         'Content-Type': 'application/json',
                         'Authorization': f'Bearer {self.qiwiApi}'})
            req = json.loads(h.text)
            count = 0
            for i in range(len(req['data'])):
               if req['data'][i]['sum']['currency'] == 643:
                    if req['data'][i]['comment'] == f"{comment}":
                        count += 1
                        amount = req['data'][i]['sum']['amount']
                        amount = round(amount)
                        Global.update(balance=Global.balance + int(amount)).where(Global.user_id == user_id).execute()
                        payBalance.update(status=True).where(payBalance.user_id == user_id).execute()
                        break
            if count == 1:
                self.send(user_id, f'[✅]Баланс успешно пополнен на {amount} рубл(я/ей)')
                self.give24pay.append(amount)
                func.updateAddQiwi(int(amount))
                self.send(self.admin_id, f'[✅]Поступил платеж[✅]\nСумма: {amount}\nПополнил: {user_id}')
                if userInfo[0].referal != 0:
                    if userInfo[0].referalPersonal != 0:
                        self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
                        Global.update(
                            balance=Global.balance + math.floor(amount / 100 * userInfo[0].referalPersonal)).where(
                            Global.user_id == userInfo[0].referal).execute()
                    else:
                        self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
                        Global.update(
                            balance=Global.balance + math.floor(int(amount) / 100 * int(func.persentRef()))).where(
                            Global.user_id == userInfo[0].referal).execute()
            else:
                self.send(user_id, f'Платеж не найден')
        except Exception as e:
            print(e)

    @func.error_decorator
    def sendQiwi(self, message):
        if message.text.isdigit():
            sumSend = self.send(message.from_user.id, 'Введите сумму для выплаты(не меньше 49)')
            self.bot.register_next_step_handler(sumSend, self.sendQiwiTwo, message.text)
        else:
            self.send(message.from_user.id, 'Неверно указан киви')

    @func.error_decorator
    def sendQiwiTwo(self, message, number):
        balance = Global.select().where(Global.user_id == message.from_user.id)[0].balance
        if message.text.isdigit():
            if balance >= int(message.text):
                if int(message.text) >= 49:
                    Global.update(balance=Global.balance - int(message.text)).where(
                        Global.user_id == message.from_user.id).execute()
                    self.send(message.from_user.id, mess.giveMoney.format(message.text, number))
                    self.send(self.admin_id,
                              mess.giveMoneyAdmin.format(message.text, number, message.from_user.username,
                                                         message.from_user.id),
                              reply_markup=keyboard.closeMessage(message.from_user.id, number, message.text))
                    try:
                        self.send(config.idMoney,
                                  mess.sendMoney.format(message.text, '@' + str(message.from_user.username)))
                    except:
                        pass
                    self.give24give.append(int(message.text))
                    func.updateReturnQiwi(int(message.text))
                else:
                    self.send(message.from_user.id, 'Минимальная сумма выплаты 49 рублей')
            else:
                self.send(message.from_user.id, 'Недостаточно средств')
        else:
            self.send(message.from_user.id, 'Сумма должна состоять из чисел')

    def serverInform(self):
        threads = ps.cpu_count(logical=False)
        lthreads = ps.cpu_count()
        RAM = ps.virtual_memory().percent
        cpu_percents = ps.cpu_percent(percpu=True)
        starttime = datetime.now() - self.startime
        cpupercents = ""
        for a in range(lthreads):
            cpupercents += "Поток : {} | Загруженность : {} %\n".format(a + 1, cpu_percents[a - 1])
        return """Загрузка систем :
Ядер : {} | Загруженность : {}%
{}Загруженность ОЗУ : {} %
Времени прошло со старта : {} """.format(threads, ps.cpu_percent(), cpupercents, RAM,
                                         "{} дней, {} часов, {} минут.".format(starttime.days,
                                                                               starttime.seconds // 3600,
                                                                               (

                                                                                       starttime.seconds % 3600) // 60))

    def statsInform(self):
        allUser = Global.select().count()
        return mess.stats.format(allUser, len(self.userDay), len(self.user), sum(self.give24pay),
                                 sum(self.give24give),
                                 func.qiwiCount(), func.qiwiReturn())