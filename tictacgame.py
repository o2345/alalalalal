import telebot
import ast
from db import GamesTicTac, Global
from asset import func
import config
from asset import text as mess
import random


class TicTacGame:
    def __init__(self, bot):
        self.bot = bot
        self.send = bot.send_message

    @func.error_decorator
    def createGame(self, message, user_id):
        if message.text.isdigit():
            if int(message.text) >= 5:
                if Global.select().where(Global.user_id == user_id)[0].balance >= int(message.text):
                    self.idGame = random.randint(100000, 9999999)
                    GamesTicTac.create(
                        idGame=self.idGame,
                        creater=user_id,
                        board=list(range(1, 10)),
                        balance=message.text
                    )
                    Global.update(balance=Global.balance - int(message.text)).where(Global.user_id == user_id).execute()
                    self.send(user_id, f'✅Игра успешно создана\n🧨Номер игры: {self.idGame}\n💵Ожидайте игрока')
                    self.send(config.idLogs, f'{mess.logsNewGame.format(message.text)} Крестики Нолики')
                else:
                    self.send(user_id, '⚠Недостаточно средств')
            else:
                self.send(user_id, '⚠Минимальная ставка 5 рублей')
        else:
            self.send(user_id, '⚠Ставка должна быть числом')

    @func.error_decorator
    def createBomb(self, user_id, text, idGame=None):
        if idGame is None:
            board = ast.literal_eval(
                GamesTicTac.select().where(GamesTicTac.idGame == self.idGame, GamesTicTac.status == False)[0].board)
        else:
            board = ast.literal_eval(
                GamesTicTac.select().where(GamesTicTac.idGame == idGame, GamesTicTac.status == False)[0].board)
            self.idGame = idGame

        bomb = telebot.types.InlineKeyboardMarkup()
        for i in range(3):
            btn = telebot.types.InlineKeyboardButton(text=board[0 + i * 3],
                                                     callback_data=f'bomb_{board[0 + i * 3]}:{self.idGame}')
            btn1 = telebot.types.InlineKeyboardButton(text=board[1 + i * 3],
                                                      callback_data=f'bomb_{board[1 + i * 3]}:{self.idGame}')
            btn2 = telebot.types.InlineKeyboardButton(text=board[2 + i * 3],
                                                      callback_data=f'bomb_{board[2 + i * 3]}:{self.idGame}')
            bomb.add(btn, btn1, btn2)
        self.send(user_id, text, reply_markup=bomb)

    def check_win(self, idGame):
        board = ast.literal_eval(
            GamesTicTac.select().where(GamesTicTac.idGame == idGame, GamesTicTac.status == False)[0].board)
        win_coord = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        for each in win_coord:
            if board[each[0]] == board[each[1]] == board[each[2]]:
                return board[each[0]]

        counter = 0
        for i in board:
            if type(i) == int:
                continue
            else:
                counter += 1
        if counter == 9:
            return counter
        else:
            return False

    @func.error_decorator
    def tic(self, idGames, num, c):
        infoGame = GamesTicTac.select().where(GamesTicTac.idGame == idGames, GamesTicTac.status == False)
        board = ast.literal_eval(infoGame[0].board)
        player_answer = int(num)
        if str(board[player_answer - 1]) != "❌⭕":
            board[player_answer - 1] = "⭕"
            GamesTicTac.update(board=board).where(GamesTicTac.idGame == idGames, GamesTicTac.status == False).execute()
        tmp = self.check_win(idGames)
        if type(tmp) == str:
            self.send(c.from_user.id, f"Результат игры: {func.userName(c.from_user.id)} выиграл!")
            try:
                self.send(c.from_user.id, f"Результат игры: {func.userName(c.from_user.id)} выиграл!")
            except:
                pass
            func.updateGlobalBalanceWin(infoGame[0].balance * 2, c.from_user.id)
            return func.setStatusGame(idGames)
        elif type(tmp) == int:
            self.send(c.from_user.id, 'Результат игры: Ничья')
            self.send(infoGame[0].gamerTwo, 'Результат игры: Ничья')
            func.returnBalance(idGames)
            return func.setStatusGame(idGames)
        else:
            self.send(c.from_user.id, 'Ожидайте хода второго пользователя')
            try:
                self.createBomb(infoGame[0].gamerTwo, 'Пользователь сделал ход', idGames)
            except:
                func.updateGlobalBalanceWin(infoGame[0].balance * 2, c.from_user.id)
                func.setStatusGame(idGames)

    @func.error_decorator
    def tac(self, idGames, num, c):
        infoGame = GamesTicTac.select().where(GamesTicTac.idGame == idGames, GamesTicTac.status == False)
        board = ast.literal_eval(infoGame[0].board)
        player_answer = int(num)
        if str(board[player_answer - 1]) not in "❌⭕":
            board[player_answer - 1] = "❌"
            GamesTicTac.update(board=board).where(GamesTicTac.idGame == idGames, GamesTicTac.status == False).execute()
        tmp = self.check_win(idGames)
        if type(tmp) == str:
            self.send(c.from_user.id, f"Результат игры: {func.userName(c.from_user.id)} выиграл!")
            try:
                self.send(c.from_user.id, f"Результат игры: {func.userName(c.from_user.id)} выиграл!")
            except:
                pass
            func.updateGlobalBalanceWin(infoGame[0].balance * 2, c.from_user.id)
            return func.setStatusGame(idGames)

        elif type(tmp) == int:
            self.send(c.from_user.id, 'Результат игры: Ничья')
            self.send(infoGame[0].creater, 'Результат игры: Ничья')
            func.returnBalance(idGames)
            return func.setStatusGame(idGames)
        else:
            self.send(c.from_user.id, 'Ожидайте хода второго пользователя')
            try:
                self.createBomb(infoGame[0].creater, 'Пользователь сделал ход', idGames)
            except:
                self.send(c.from_user.id, 'Вы выйграли так как пользователь отказался играть!')
                func.updateGlobalBalanceWin(infoGame[0].balance * 2, c.from_user.id)
                func.setStatusGame(idGames)

    @func.error_decorator
    def connectTicTac(self, idGames, user_id):
        infoGame = GamesTicTac.select().where(GamesTicTac.idGame == idGames, GamesTicTac.gamerTwo == 0,
                                              GamesTicTac.status == False)
        if infoGame.exists():
            if infoGame[0].creater != user_id:
                if Global.select().where(Global.user_id == user_id)[0].balance >= infoGame[0].balance:
                    func.updateStatGame(infoGame[0].balance)
                    GamesTicTac.update(gamerTwo=user_id).where(GamesTicTac.idGame == idGames).execute()
                    self.send(user_id, f'Создатель игры: {Global.select().where(Global.user_id == infoGame[0].creater)[0].username}')
                    self.createBomb(user_id, text='Ваш ход, выберите клетку', idGame=idGames)
                    try:
                        self.send(infoGame[0].creater, f'К вам подключился игрок: {func.userName(user_id)}\nОжидайте свой ход')
                    except:
                        self.send(user_id, '💢Создатель отменил игру\nСредства не списаны')
                        return
                    Global.update(balance=Global.balance - infoGame[0].balance).where(Global.user_id == user_id).execute()
                else:
                    self.send(user_id, '⚠Недостаточно средств')
            else:
                self.send(user_id, '⚠Нельзя подключится к своей игре!')
        else:
            self.send(user_id, '⚠Список игр', reply_markup=self.allGame())

    def allGame(self):
        infoGame = GamesTicTac.select().where(GamesTicTac.gamerTwo == 0, GamesTicTac.status == False)
        markup = telebot.types.InlineKeyboardMarkup()
        for info in infoGame:
            btn = telebot.types.InlineKeyboardButton(text=f'💢 Game_{info.idGame} | {info.balance} р 💢',
                                                     callback_data=f'connectTic_{info.idGame}')
            markup.add(btn)
        reloadBtn = telebot.types.InlineKeyboardButton(text='💢Обновить', callback_data='reloadTicTac')
        createBtn = telebot.types.InlineKeyboardButton(text='🤩Создать игру', callback_data='createTicTac')
        myGame = telebot.types.InlineKeyboardButton(text='🧨Мои игры', callback_data='delGameTicTac')
        markup.add(createBtn, reloadBtn)
        markup.add(myGame)
        return markup