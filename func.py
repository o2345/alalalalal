# -*- coding: utf-8 -*-

from db import *
import math
import traceback
import sys


def userName(user_id):
    user = Global.select().where(Global.user_id == user_id)[0].username
    if userName is None:
        return user_id
    else:
        return user


def statBase():
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'statGame' == val.rstrip():
                game = lines[i + 1][6:].rstrip()
                balance = lines[i + 2][9:].rstrip()
                return game, balance


def persentGive():
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'setting' == val.rstrip():
                com = lines[i + 1][11:].rstrip()
                return com


def persentRef():
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'setting' == val.rstrip():
                com = lines[i + 2][9:].rstrip()
                return com


def qiwiCount():
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'statGame' == val.rstrip():
                com = lines[i + 3][6:].rstrip()
                return com


def qiwiReturn():
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'statGame' == val.rstrip():
                com = lines[i + 4][10:].rstrip()
                return com


def updateReturnQiwi(balance):
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'statGame' == val.rstrip():
                qiwi = lines[i + 4][10:].rstrip()
                lines[i+4] = lines[i+4][:10]+str(balance + int(qiwi)) + '\n'
    with open('asset/stat.txt', 'r+') as filename:
        filename.writelines(lines)


def updateAddQiwi(balance):
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'statGame' == val.rstrip():
                qiwi = lines[i + 3][6:].rstrip()
                lines[i+3] = lines[i+3][:6]+str(balance + int(qiwi)) + '\n'
    with open('asset/stat.txt', 'r+') as filename:
        filename.writelines(lines)


def updateAddRef(ref):
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'setting' == val.rstrip():
                lines[i+1] = lines[i+1][:11]+str(ref) + '\n'
    with open('asset/stat.txt', 'r+') as filename:
        filename.writelines(lines)


def updateAddRefPer(ref):
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'setting' == val.rstrip():
                lines[i+2] = lines[i+2][:9]+str(ref) + '\n'
    with open('asset/stat.txt', 'r+') as filename:
        filename.writelines(lines)


def updateStatGame(balance):
    with open('asset/stat.txt', 'r') as filename:
        lines = filename.readlines()
        for i, val in enumerate(lines):
            if 'statGame' == val.rstrip():
                game = int(lines[i+1][6:].rstrip())
                balances = lines[i + 2][9:].rstrip()
                lines[i+1] = lines[i+1][:6]+str(game + 1) + '\n'
                lines[i + 2] = lines[i + 2][:9] + str(int(balances) + balance) + '\n'
    with open('asset/stat.txt', 'r+') as filename:
        filename.writelines(lines)


def updateGlobalBalanceWin(balance, user_id):
    persent = int(persentGive())
    count = balance/100*persent
    result = balance - count
    Global.update(balance=Global.balance + math.floor(result), countWin=Global.countWin + 1).where(
        Global.user_id == user_id).execute()


def gameResult(balance):
    persent = int(persentGive())
    count = balance / 100 * persent
    result = balance - count
    return math.floor(result)


def error_decorator(func):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f'Произошла ошибка: {e} в функции {func}')
            for frame in traceback.extract_tb(sys.exc_info()[2]):
                fname, lineno, fn, text = frame
                print("Error in %s on line %d" % (fname, lineno))
    return wrap


def returnBalance(idGames):
    infoGame = GamesTicTac.select().where(GamesTicTac.idGame == idGames, GamesTicTac.status == False)
    Global.update(balance=Global.balance + infoGame[0].balance).where(Global.user_id == infoGame[0].creater).execute()
    Global.update(balance=Global.balance + infoGame[0].balance).where(
        Global.user_id == infoGame[0].gamerTwo).execute()


def setStatusGame(idGames):
    GamesTicTac.update(status=True).where(GamesTicTac.idGame == idGames,
                                          GamesTicTac.status == False).execute()