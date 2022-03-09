from telebot import types
from db import *
from config import *

createGame = types.InlineKeyboardButton(text='🔥Создать игру', callback_data='createGame')
reloadGame = types.InlineKeyboardButton(text='♻Обновить', callback_data='reloadGame')
myGame = types.InlineKeyboardButton(text='😎Мои игры', callback_data='myGame')
backBtn = types.InlineKeyboardButton(text='⬅Назад', callback_data='back')

menuUser = types.ReplyKeyboardMarkup(True, False)
menuUser.add('🌪Игры')
menuUser.add('🖥 Кабинет', '📜 Информация')
menuUser.add('⚠Помощь⚠')

menuGame = types.ReplyKeyboardMarkup(True, False)
menuGame.add('😎21 Очко', '✅Крестики, Нолики')
menuGame.add('🔥Вернуться назад🔥')


reloadKey = types.InlineKeyboardMarkup()
reloadKey.add(reloadGame)

adminPanel = types.ReplyKeyboardMarkup(True, False)
adminPanel.add('Управление пользователями')
adminPanel.add('Информация по боту')
adminPanel.add('Управление Qiwi')
adminPanel.add('Управление промо')
adminPanel.add('Рассылка')
adminPanel.add('Назад')

cancelButton = types.ReplyKeyboardMarkup(True, False)
cancelButton.add('💢Отмена💢')

usersAdm = types.ReplyKeyboardMarkup(True, False)
usersAdm.add('Выдать баланс', 'Забрать баланс')
usersAdm.add('Выдать админа', 'Забрать админа')
usersAdm.add('Поставить реф.процент', 'Удалить игру')
usersAdm.add('Реф.процент', 'Изменить реф.процент')
usersAdm.add('Ком.процент', 'Изменить ком.процент')
usersAdm.add('Информация на пользователя')
usersAdm.add('<<<Назад')

qiwiAdm = types.ReplyKeyboardMarkup(True, False)
qiwiAdm.add('Баланс Qiwi', 'Вывести деньги')
qiwiAdm.add('<<<Назад')

informAdmin = types.ReplyKeyboardMarkup(True, False)
informAdmin.add('Сервер', 'Статистика')
informAdmin.add('<<<Назад')


def gameAll():
    game = types.InlineKeyboardMarkup()
    for i in Games.select().where(Games.gamerTwo == 0):
        gameBtn1 = types.InlineKeyboardButton(text=f'💢 #Game_{i.id} | Сумма {i.balance}р',
                                              callback_data=f'gameCon_{i.id}')
        game.add(gameBtn1)
    game.add(myGame, reloadGame)
    game.add(createGame)
    return game


def gameUser(user_id):
    game = types.InlineKeyboardMarkup()
    for i in Games.select().where(Games.user_id == user_id):
        if i.gamerTwo == 0:
            gameBtn1 = types.InlineKeyboardButton(text=f'Сумма {i.balance}р | 💢Отмена',
                                                  callback_data=f'gameDel_{i.id}')
            game.add(gameBtn1)
    game.add(backBtn)
    return game


def keyFirst(id):
    gameStart = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='Взять еще', callback_data=f'firstAdd_{id}')
    btn2 = types.InlineKeyboardButton(text='Хватит, пусть играет', callback_data=f'firstGive_{id}')
    gameStart.add(btn)
    gameStart.add(btn2)
    return gameStart


def keyTwo(id):
    gameStart = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='Взять еще', callback_data=f'twoAdd_{id}')
    btn2 = types.InlineKeyboardButton(text='Хватит, вскрываемся', callback_data=f'allIn_{id}')
    gameStart.add(btn)
    gameStart.add(btn2)
    return gameStart


cabinet = types.InlineKeyboardMarkup()
cabinetBal = types.InlineKeyboardButton(text='⚜Пополнить баланс', callback_data='addBalance')
cabinetGive = types.InlineKeyboardButton(text='⚜Вывод средств', callback_data='giveMoney')
referalSys = types.InlineKeyboardButton(text='👥Реферальная система', callback_data='refSys')
cabinet.add(cabinetBal, cabinetGive)
cabinet.add(referalSys)


def linkPay(comment):
    urlPay1 = urlPay.replace('{num}', str(number)).replace('{com}', str(comment))
    autoPay = types.InlineKeyboardMarkup(row_width=1)
    checkPay = types.InlineKeyboardButton(text='Проверить оплату', callback_data='checkPay')
    keyLink = types.InlineKeyboardButton(text='Оплата', url=urlPay1)
    autoPay.add(checkPay, keyLink)
    return autoPay


def informKeyboard():
    markup = types.InlineKeyboardMarkup()
    topUser = types.InlineKeyboardButton(text='🧨Топ 10 игроков', callback_data='top10')
    help = types.InlineKeyboardButton(text='✅Поддержка', url=f't.me/{linkTg[1:]}')
    rulesGame = types.InlineKeyboardButton(text='📕Правила игры',
                                           url='https://telegra.ph/Dvadcat-odno-21Ochko--Pravila-08-22')
    logsBtn = types.InlineKeyboardButton(text='💎Логи', url=linkLogs)
    chatMoneyBtn = types.InlineKeyboardButton(text='💶Выплаты', url=linkMoney)
    chatUser = types.InlineKeyboardButton(text='📁Чат', url=chatUsers)
    markup.add(topUser)
    markup.add(chatUser, help)
    markup.add(logsBtn, chatMoneyBtn)
    markup.add(rulesGame)
    return markup


def top10gamers():
    gamers = Global.select().where(Global.username != '@None').order_by(Global.countWin.desc(),
                                                                         Global.countBad.asc()).limit(10)
    markup = types.InlineKeyboardMarkup()
    backBtn2 = types.InlineKeyboardButton(text='⬅Назад', callback_data='back2')
    for i in gamers:
        btn = types.InlineKeyboardButton(text=f'ℹ{i.username[1:]} |🕹{i.countWin + i.countBad} Игры |🏆{i.countWin} Победы |☹{i.countBad} Проигрыши', url=f't.me/{i.username[1:]}')
        markup.add(btn)
    markup.add(backBtn2)
    return markup


def payment():
    markup = types.InlineKeyboardMarkup()
    qiwi = types.InlineKeyboardButton(text='⚜QIWI', callback_data='addBalanceQiwi')
    btc = types.InlineKeyboardButton(text='⚜BTC | БАНКИР', callback_data='addBalanceBtc')
    promo = types.InlineKeyboardButton(text='💵Промо-код💵', callback_data='promoActivate')
    markup.add(qiwi, btc)
    markup.add(promo)
    return markup


def closeMessage(user_id, phone, count):
    markup = types.InlineKeyboardMarkup()
    btnSendMoney = types.InlineKeyboardButton(text='Выплатить', callback_data=f'send_{user_id}:{phone}:{count}')
    btnBackMoney = types.InlineKeyboardButton(text='Вернуть деньги', callback_data=f'backMoney_{user_id}:{count}')
    btnClose = types.InlineKeyboardButton(text='Закрыть', callback_data='closeMessage')
    markup.add(btnSendMoney)
    markup.add(btnBackMoney)
    markup.add(btnClose)
    return markup


def gameAdminDelete():
    game = types.InlineKeyboardMarkup()
    for i in Games.select().where(Games.gamerTwo == 0):
        gameBtn1 = types.InlineKeyboardButton(text=f'Сумма {i.balance}р | 💢Отмена',
                                              callback_data=f'gameDelAdmin_{i.id}')
        game.add(gameBtn1)
    game.add(backBtn)
    return game


def promoRemoute():
    markup = types.InlineKeyboardMarkup()
    addPromo = types.InlineKeyboardButton(text='Создать промо', callback_data='createPromo')
    delPromo = types.InlineKeyboardButton(text='Удалить промо', callback_data='deletePromo')
    activePromo = types.InlineKeyboardButton(text=f'Активные промо', callback_data='activePromo')
    markup.add(addPromo, delPromo)
    markup.add(activePromo)
    return markup