from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase("database/db.db")


class Global(Model):
    id = PrimaryKeyField(null=False)
    user_id = IntegerField(null=False)
    username = TextField(null=False)
    countWin = IntegerField(default=0)
    countBad = IntegerField(default=0)
    class Meta:
        db_table = 'Users'
        database = db

class GamesTicTac(Model):
    id = PrimaryKeyField(null=False)
    idGame = IntegerField(null=False)
    creater = IntegerField(null=False)
    setNow = IntegerField(default=creater)
    board = TextField(null=False)

    class Meta:
        db_table = 'gametictac'
        database = db

def con():
    try:
        GamesTicTac.create_table()
        print('База данных GamesTicTac успешно загружена')
    except InternalError as px:
        print(str(px))
        raise