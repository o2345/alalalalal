from db import Global, Games, Promo
from asset import func
from asset import keyboard
import config
import ast
from asset import text as mess
import random


class usersCommandHandler:
    """Инициализация класса функции пользователей"""
    def __init__(self, bot):
        self.bot = bot
        self.send = bot.send_message

    @func.error_decorator
    def gameCreate(self, message):
        infoUser = Global.select().where(Global.user_id == message.from_user.id)
        user_id = message.from_user.id
        if message.text.isdigit():
            if infoUser[0].balance >= int(message.text):
                if int(message.text) > 5:
                    koloda = [7, 8, 9, 10, 2, 3, 4, 11] * 4
                    random.shuffle(koloda)
                    Games.create(
                        user_id=message.from_user.id,
                        balance=int(message.text),
                        card=koloda,
                    )
                    Global.update(balance=Global.balance - int(message.text)).where(Global.user_id == user_id).execute()
                    self.send(config.idLogs, mess.logsNewGame.format(message.text))
                    self.send(user_id, 'Игра успешно создана')
                else:
                    self.send(user_id, 'Ставка на игру должна быть больше 5')
            else:
                self.send(user_id, 'Недостаточно средств')
        else:
            self.send(user_id, 'Сумма состоит из цифр')

    @func.error_decorator
    def connectGame(self, user_id, id):
        infoGame = Games.select().where(Games.id == id)
        userInfo = Global.select().where(Global.user_id == user_id)
        if infoGame[0].gamerTwo == 0:
            if infoGame[0].user_id != user_id:
                if userInfo[0].balance >= infoGame[0].balance:
                    Games.update(gamerTwo=user_id).where(Games.id == id).execute()
                    card = Games.select().where(Games.id == id)[0].card
                    card = ast.literal_eval(card)
                    count = card.pop()
                    Games.update(card=card, gamerTwoCount=count).where(Games.id == id).execute()
                    try:
                        self.send(user_id,
                                  mess.connectGame.format(id, infoGame[0].balance, func.userName(infoGame[0].user_id)))
                    except:
                        pass
                    try:
                        self.send(user_id, mess.card.format(1, count), reply_markup=keyboard.keyFirst(id))
                    except:
                        pass
                    card = Games.select().where(Games.id == id)[0].card
                    card = ast.literal_eval(card)
                    count = card.pop()
                    Games.update(gamerTwo=user_id).where(Games.id == id).execute()
                    Games.update(card=card, gamerFirstCount=count).where(Games.id == id).execute()
                    Global.update(balance=Global.balance - infoGame[0].balance).where(
                        Global.user_id == user_id).execute()
                    try:
                        self.send(infoGame[0].user_id,
                                  mess.gameConnectTwo.format(userInfo[0].username, id, infoGame[0].balance))
                    except:
                        pass
                else:
                    self.send(user_id, 'Недостаточно денег')
            else:
                self.send(user_id, 'Нельзя подключится к своей игре!')
        else:
            self.send(user_id, 'Игры не сущеcтвует', reply_markup=keyboard.reloadGame)

    @func.error_decorator
    def firstAddCard(self, id, user_id, data):
        infoGame = Games.select().where(Games.id == id)
        infoPlayerFirst = Global.select().where(Global.user_id == user_id)
        card = infoGame[0].card
        card = ast.literal_eval(card)
        count = random.choice(card)
        card.remove(count)
        Games.update(card=card).where(Games.id == id).execute()
        if (infoGame[0].gamerTwoCount + count) > 21:
            self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            self.send(user_id, mess.machCard.format(func.userName(infoGame[0].user_id)))
            func.updateGlobalBalanceWin(infoGame[0].balance * 2, infoGame[0].user_id)
            self.send(infoGame[0].user_id,
                      mess.vinGameMach.format(f'{infoGame[0].balance * 2}', func.userName(infoGame[0].gamerTwo)))
            self.send(config.idLogs,
                      mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                          func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount + count,
                                          func.userName(infoGame[0].user_id), func.gameResult(infoGame[0].balance * 2)))
            Global.update(countBad=Global.countBad + 1).where(Global.user_id == user_id).execute()
            func.updateStatGame(infoGame[0].balance * 2)
        else:
            self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            Games.update(gamerTwoCount=Games.gamerTwoCount + count, gamerTwoCard=Games.gamerTwoCard + 1).where(
                Games.id == id).execute()
            self.send(user_id, mess.card.format(infoGame[0].gamerTwoCard + 1, infoGame[0].gamerTwoCount + count),
                      reply_markup=keyboard.keyFirst(id))
            self.send(infoGame[0].user_id, mess.addCard.format(infoPlayerFirst[0].username))

    @func.error_decorator
    def twoAddCard(self, id, user_id, data):
        infoGame = Games.select().where(Games.id == id)
        infoPlayerFirst = Global.select().where(Global.user_id == user_id)
        card = infoGame[0].card
        card = ast.literal_eval(card)
        count = random.choice(card)
        card.remove(count)
        Games.update(card=card).where(Games.id == id).execute()
        if (infoGame[0].gamerFirstCount + count) > 21:
            try:
                self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            except:
                pass
            self.send(user_id, mess.machCard.format(infoGame[0].gamerTwo))
            func.updateGlobalBalanceWin(func.gameResult(infoGame[0].balance * 2), infoGame[0].gamerTwo)
            try:
                self.send(infoGame[0].gamerTwo,
                          mess.vinGameMach.format(f'{func.gameResult(infoGame[0].balance * 2)}',
                                                  func.userName(infoGame[0].user_id)))
            except:
                pass
            try:
                self.send(config.idLogs,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount + count,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].gamerTwo),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            Global.update(countBad=Global.countBad + 1).where(Global.user_id == user_id).execute()
            func.updateStatGame(infoGame[0].balance * 2)
        else:
            self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            Games.update(gamerFirstCount=Games.gamerFirstCount + count, gamerFirstCard=Games.gamerFirstCard + 1).where(
                Games.id == id).execute()
            self.send(user_id, mess.card.format(infoGame[0].gamerFirstCard + 1, infoGame[0].gamerFirstCount + count),
                      reply_markup=keyboard.keyTwo(id))
            self.send(infoGame[0].gamerTwo, mess.addCard.format(infoPlayerFirst[0].username))

    def firstGive(self, id, user_id, data):
        infoGame = Games.select().where(Games.id == id)
        infoUser = Global.select().where(Global.user_id == user_id)
        self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
        try:
            self.send(infoGame[0].user_id, mess.stopGameFirst.format(infoUser[0].username, infoGame[0].gamerTwoCard))
            self.send(infoGame[0].user_id, mess.card.format(1, infoGame[0].gamerFirstCount),
                      reply_markup=keyboard.keyTwo(id))
        except Exception as e:
            pass

    @func.error_decorator
    def allIn(self, id, user_id, data):
        infoGame = Games.select().where(Games.id == id)
        func.updateStatGame(infoGame[0].balance * 2)
        if infoGame[0].gamerFirstCount == infoGame[0].gamerTwoCount:
            self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            self.send(user_id, mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                                   func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                                   func.userName(infoGame[0].user_id),
                                                   func.gameResult(infoGame[0].balance * 2)))
            try:
                self.send(infoGame[0].gamerTwo,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].user_id),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            try:
                self.send(config.idLogs,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].user_id),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            func.updateGlobalBalanceWin(infoGame[0].balance * 2, infoGame[0].user_id)
            Global.update(countBad=Global.countBad + 1).where(Global.user_id == infoGame[0].gamerTwo).execute()
            return
        elif infoGame[0].gamerFirstCount > infoGame[0].gamerTwoCount:
            func.updateGlobalBalanceWin(infoGame[0].balance * 2, infoGame[0].user_id)
            Global.update(countBad=Global.countBad + 1).where(Global.user_id == infoGame[0].gamerTwo).execute()
            self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            self.send(user_id, mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                                   func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                                   func.userName(infoGame[0].user_id),
                                                   func.gameResult(infoGame[0].balance * 2)))
            try:
                self.send(infoGame[0].gamerTwo,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].user_id),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            try:
                self.send(config.idLogs,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].user_id),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            return
        elif infoGame[0].gamerFirstCount < infoGame[0].gamerTwoCount:
            self.bot.delete_message(chat_id=user_id, message_id=data.message.message_id)
            self.send(user_id, mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                                   func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                                   func.userName(infoGame[0].gamerTwo),
                                                   func.gameResult(infoGame[0].balance * 2)))
            func.updateGlobalBalanceWin(infoGame[0].balance * 2, infoGame[0].gamerTwo)
            Global.update(countBad=Global.countBad + 1).where(Global.user_id == user_id).execute()
            try:
                self.send(infoGame[0].gamerTwo,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].gamerTwo),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            try:
                self.send(config.idLogs,
                          mess.winGame.format(func.userName(infoGame[0].user_id), infoGame[0].gamerFirstCount,
                                              func.userName(infoGame[0].gamerTwo), infoGame[0].gamerTwoCount,
                                              func.userName(infoGame[0].gamerTwo),
                                              func.gameResult(infoGame[0].balance * 2)))
            except:
                pass
            return

    @func.error_decorator
    def dellGame(self, id, user_id, data):
        infoGame = Games.select().where(Games.id == id)
        if infoGame[0].gamerTwo == 0:
            Games.delete().where(Games.id == id).execute()
            self.bot.edit_message_text(chat_id=user_id, message_id=data.message.message_id, text='Игра успешно удалена')
            Global.update(balance=Global.balance + infoGame[0].balance).where(Global.user_id == user_id).execute()
        else:
            self.bot.edit_message_text(chat_id=user_id, message_id=data.message.message_id,
                                       text='Нельзя удалить начатую игру')

    @func.error_decorator
    def promoActivate(self, message):
        infoPromo = Promo.select().where(Promo.promo == message.text)
        if infoPromo.exists():
            if infoPromo[0].count > 0:
                usersActivate = ast.literal_eval(infoPromo[0].users)
                if message.from_user.id not in usersActivate:
                    usersActivate.append(message.from_user.id)
                    Global.update(balance=Global.balance + infoPromo[0].balance).where(
                        Global.user_id == message.from_user.id).execute()
                    Promo.update(users=usersActivate, count=Promo.count - 1).where(
                        Promo.promo == message.text).execute()
                    self.send(message.from_user.id, mess.promoActivate.format(infoPromo[0].balance))
                    user = Global.select().where(Global.user_id == message.from_user.id)
                    self.send(config.admin_id, mess.logPromo.format(message.text, user[0].username, message.from_user.id))
                else:
                    self.send(message.from_user.id, 'Вы уже активировали этот промо-код')
            else:
                self.send(message.from_user.id, 'Промо-код закончился')
        else:
            self.send(message.from_user.id, 'Промо-кода не существует')