# -*- coding: utf-8 -*-

from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase("database/db.db")


class Global(Model):
    id = PrimaryKeyField(null=False)
    user_id = IntegerField(null=False)
    username = TextField(null=False)
    balance = IntegerField(default=0)
    countWin = IntegerField(default=0)
    countBad = IntegerField(default=0)
    referal = IntegerField(default=0)
    referalCount = IntegerField(default=0)
    referalPersonal = IntegerField(default=0)
    adm = IntegerField(default=0)

    class Meta:
        db_table = 'Users'
        database = db


class Games(Model):
    id = PrimaryKeyField(null=False)
    user_id = IntegerField(null=False)
    gamerFirstCount = IntegerField(default=0)
    gamerFirstCard = IntegerField(default=1)
    balance = IntegerField(null=False)
    gamerTwo = IntegerField(default=0)
    gamerTwoCount = IntegerField(default=0)
    gamerTwoCard = IntegerField(default=1)
    card = TextField(null=False)

    class Meta:
        db_table = 'games'
        database = db


class payBalance(Model):
    id = PrimaryKeyField(null=False)
    user_id = IntegerField(null=False)
    comment = IntegerField(null=False)
    status = BooleanField(default=False)

    class Meta:
        db_table = 'Payment'
        database = db


class Promo(Model):
    id = PrimaryKeyField(null=False)
    promo = TextField(null=False)
    count = IntegerField(null=False)
    balance = IntegerField(null=False)
    users = TextField(default='[]')

    class Meta:
        db_table = 'Promo'
        database = db


class GamesTicTac(Model):
    id = PrimaryKeyField(null=False)
    idGame = IntegerField(null=False)
    creater = IntegerField(null=False)
    gamerTwo = IntegerField(default=0)
    setNow = IntegerField(default=creater)
    board = TextField(null=False)
    balance = IntegerField(null=False)
    status = BooleanField(default=False)

    class Meta:
        db_table = 'gametictac'
        database = db

def con():
    try:
        db.connect()
        Global.create_table()
        print('База данных Users успешно загружена')
    except InternalError as px:
        print(str(px))
        raise
    try:
        Games.create_table()
        print('База данных Games успешно загружена')
    except InternalError as px:
        print(str(px))
        raise
    try:
        payBalance.create_table()
        print('База данных payBalance успешно загружена')
    except InternalError as px:
        print(str(px))
        raise
    try:
        Promo.create_table()
        print('База данных Promo успешно загружена')
    except InternalError as px:
        print(str(px))
        raise
    try:
        GamesTicTac.create_table()
        print('База данных GamesTicTac успешно загружена')
    except InternalError as px:
        print(str(px))
        raise