import vkbot
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
                if Global.select().where(Global.user_id == user_id)[0]:
                    self.idGame = random.randint(100000, 9999999)
                    GamesTicTac.create(
                        idGame=self.idGame,
                        creater=user_id,
                        board=list(range(1, 10))  
                        )
                    
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

def check_win(board):
    win_coord = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
    for each in win_coord:
        if board[each[0]] == board[each[1]] == board[each[2]]:
            return board[each[0]]
    return False

def main(board):
    counter = 0
    win = False
    while not win:
        draw_board(board)
        if counter % 2 == 0:
            take_input("X")
        else:
            take_input("O")
        counter += 1
        if counter > 4:
            tmp = check_win(board)
            if tmp:
                print (tmp, "выиграл!")
                win = True
                break
        if counter == 9:
            print ("Ничья!")
            break
    draw_board(board)

main(board)

def take_input(player_token):
    valid = False
    while not valid:
        player_answer = input("Куда поставим " + player_token+"? ")
        try:
            player_answer = int(player_answer)
        except:
            self.send(c.from_user.id, f"Некорректный ввод. Вы уверены, что ввели число?")
            continue
        if player_answer >= 1 and player_answer <= 9:
            if (str(board[player_answer-1]) not in "XO"):
                board[player_answer-1] = player_token
                valid = True
            else:
                self.send(c.from_user.id, f"Эта клеточка уже занята")
        else:
            self.send(c.from_user.id, f"Некорректный ввод. Введите число от 1 до 9 чтобы походить.")
