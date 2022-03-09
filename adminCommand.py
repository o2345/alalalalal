from db import Promo, Global, Games
from asset import func
from asset import keyboard
from asset import text as mess
from threading import Thread
from SimpleQIWI import *
from config import tokenQiwi, number


class adminCommandHandler:
    """Инициализация комманд администраторов"""
    def __init__(self, bot):
        self.bot = bot
        self.send = bot.send_message
        self.api = QApi(token=tokenQiwi, phone=number)

    @func.error_decorator
    def deletePromo(self, message):
        infoPromo = Promo.select().where(Promo.promo == message.text)
        if infoPromo.exists():
            Promo.delete().where(Promo.promo == message.text).execute()
            self.send(message.from_user.id, 'Промо-код успешно удален')
        else:
            self.send(message.from_user.id, 'Промо-кода не существует')
        self.send(message.from_user.id, 'Выберите действие', reply_markup=keyboard.promoRemoute())

    @func.error_decorator
    def deleteGameAdmin(self, idGame, user_id):
        infoGame = Games.select().where(Games.id == idGame)
        if infoGame.exists():
            if infoGame[0].gamerTwo == 0:
                Games.delete().where(Games.id == idGame).execute()
                Global.update(balance=Global.balance + infoGame[0].balance).where(
                    Global.user_id == infoGame[0].user_id).execute()
                self.send(user_id, f'Игра с id: {idGame} успешно удалена')
            else:
                self.send(user_id, 'Нельзя удалять начатую игру')
        else:
            self.send(user_id, 'Игра уже была удалена')

    @func.error_decorator
    def giveAdmin(self, message):
        if message.text.isdigit():
            userInfo = Global.select().where(Global.user_id == message.text)
            if userInfo.exists():
                Global.update(adm=True).where(Global.user_id == message.text).execute()
                self.send(message.from_user.id, 'Успешно выдан администратор!')
            else:
                self.send(message.from_user.id, 'Пользователь не найден')
        else:
            self.send(message.from_user.id, 'Id пользователя состоит из цифр')

    @func.error_decorator
    def sendMoney(self, args, data):
        if int(self.api.balance[0]) >= int(args[2]):
            self.api.pay(account=args[1], amount=int(args[2]),
                         comment=f'Выплата от бота: @{self.bot.get_me().username}\nДля пользователя: {args[0]}')
            self.bot.delete_message(chat_id=data.from_user.id, message_id=data.message.message_id)
            self.send(data.from_user.id, 'Выплата прошла успешно!')
        else:
            self.send(data.from_user.id, f'Не хватает денег на вашем кошельке баланс: {self.api.balance}')

    @func.error_decorator
    def backMoney(self, args, data):
        userInfo = Global.select().where(Global.user_id == args[0])
        if userInfo.exists():
            Global.update(balance=Global.balance + int(args[1])).where(Global.user_id == args[0]).execute()
            self.bot.delete_message(chat_id=data.from_user.id, message_id=data.message.message_id)
            self.send(data.from_user.id, 'Баланс успешно возвращен')
            try:
                self.send(int(args[0]), 'Администратор отказал вам в выплате, средства возвращены обратно на баланс')
            except:
                pass
        else:
            self.bot.delete_message(chat_id=data.from_user.id, message_id=data.message.message_id)
            self.send(data.from_user.id, 'Пользватель не найден')

    @func.error_decorator
    def promoCreateFirst(self, message):
        info = Promo.select().where(Promo.promo == message.text)
        if not info.exists():
            count = self.send(message.from_user.id, 'Введите кол-во активаций: ')
            self.bot.register_next_step_handler(count, self.promoCreateTwo, message.text)
        else:
            self.send(message.from_user.id, 'Промо-код существует!')

    @func.error_decorator
    def promoCreateTwo(self, message, promo):
        if message.text.isdigit():
            reger = [message.text, promo]
            balance = self.send(message.from_user.id, 'Введите баланс промо-кода: ')
            self.bot.register_next_step_handler(balance, self.promoCreateThree, reger)
        else:
            self.send(message.from_user.id, 'Кол-во активаций состоит из цифр')

    @func.error_decorator
    def promoCreateThree(self, message, reger):
        if message.text.isdigit():
            if int(message.text) > 0:
                Promo.create(
                    promo=reger[1],
                    count=int(reger[0]),
                    balance=int(message.text),
                )
                self.send(message.from_user.id, mess.promoCreate.format(reger[1], message.text, reger[0]))
            else:
                self.send(message.from_user.id, 'Баланс промо-кода должен быть больше 0 ')
        else:
            self.send(message.from_user.id, 'Баланс промо-кода состоит из цифр!')
        self.send(message.from_user.id, 'Выберите действие', reply_markup=keyboard.promoRemoute())

    @func.error_decorator
    def informUsers(self, message):
        Thread(target=self.statsResult, args=(message, message.text)).start()

    @func.error_decorator
    def statsResult(self, message, text):
        if message.text.isdigit():
            infoUser = Global.select().where(Global.user_id == message.text)
            if infoUser.exists():
                self.send(message.from_user.id,
                          mess.informUser.format(message.text, infoUser[0].username, infoUser[0].referalCount,
                                                 infoUser[0].balance, (infoUser[0].countWin + infoUser[0].countBad),
                                                 infoUser[0].countWin,
                                                 infoUser[0].countBad))
            else:
                self.send(message.from_user.id, 'Пользователь не найден')
        else:
            infoUser = Global.select().where(Global.username == message.text)
            if infoUser.exists():
                self.send(message.from_user.id,
                          mess.informUser.format(infoUser[0].user_id, infoUser[0].username, infoUser[0].referalCount,
                                                 (infoUser[0].countWin + infoUser[0].countBad), infoUser[0].balance,
                                                 infoUser[0].countWin,
                                                 infoUser[0].countBad))
            else:
                self.send(message.from_user.id, 'Пользователь не найден')

    @func.error_decorator
    def sendQiwiAdmFirst(self, message):
        if message.text.isdigit():
            count = self.send(message.from_user.id, f'Введите сумму для вывода(макс {self.api.balance[0]}): ')
            self.bot.register_next_step_handler(count, self.sendQiwiAdmTwo, message.text)
        else:
            self.send(message.from_user.id, 'Не верно введен номер!')

    @func.error_decorator
    def sendQiwiAdmTwo(self, message, number):
        if message.text.isdigit():
            if int(message.text) < int(self.api.balance[0]):
                self.api.pay(account=number, amount=int(message.text))
                self.send(message.from_user.id, 'Успешный вывод средств')
            else:
                self.send(message.from_user.id, 'Недостаточно средств')
        else:
            self.send(message.from_user.id, 'Сумма должна быть указана в цифрах')

    @func.error_decorator
    def giveBalanceFirst(self, message):
        if message.text.isdigit():
            if Global.select().where(Global.user_id == message.text).exists():
                addBalance = self.send(message.from_user.id, '[✅]А теперь введите сумму: ')
                self.bot.register_next_step_handler(addBalance, self.giveBalanceTwo, message.text)
            else:
                self.send(message.from_user.id, '[🚫]Пользователя не существует', reply_markup=keyboard.adminPanel)
        elif message.text == '💢Отмена💢':
            self.send(message.from_user.id, '[❗]Действие отменено', reply_markup=keyboard.adminPanel)
        else:
            self.send(message.from_user.id, '[❗]Id пользователя состоит из цифр', reply_markup=keyboard.adminPanel)

    @func.error_decorator
    def giveBalanceTwo(self, message, user_id):
        if message.text.isdigit():
            Global.update(balance=Global.balance + int(message.text)).where(Global.user_id == user_id).execute()
            self.send(message.from_user.id,
                      f'[✅]Вы успешно выдали баланс пользователю {user_id}\nВыдали: {message.text}',
                      reply_markup=keyboard.adminPanel)
            try:
                self.send(user_id, f'[✅]Вам выдали {message.text} рублей на баланс')
            except Exception as e:
                pass
        elif message.text == '💢Отмена💢':
            self.send(message.from_user.id, '[❗]Действие отменено', reply_markup=keyboard.adminPanel)
        else:
            self.send(message.from_user.id, '[❗]Сумма состоит из цифр', reply_markup=keyboard.adminPanel)

    @func.error_decorator
    def refPersNew(self, message):
        if message.text.isdigit():
            if int(message.text) < 100:
                func.updateAddRefPer(int(message.text))
                self.send(message.from_user.id, 'Успешно обновление')
            else:
                self.send(message.from_user.id, 'Нельзя указывать больше 100 или равное 100')
        else:
            self.send(message.from_user.id, 'Вы ввели не число')

    @func.error_decorator
    def rassulkaStart(self, message):
        if message.text == '💢Отмена💢':
            self.send(message.from_user.id, '[❗]Действие отменено', reply_markup=keyboard.adminPanel)
        else:
            photo = self.send(message.from_user.id, 'Отправьте фото если нужно, если нет введите любой текст: ')
            self.bot.register_next_step_handler(photo, self.rassulka, message.text)

    @func.error_decorator
    def refComNew(self, message):
        if message.text.isdigit():
            func.updateAddRef(message.text)
            self.send(message.from_user.id, 'Успешно обновление коммисионого %')
        else:
            self.send(message.from_user.id, 'Процент состоит из числа')

    @func.error_decorator
    def rassulka(self, message, text):
        banned = 0
        good = 0
        info = Global.select(Global.user_id)
        if message.text == '💢Отмена💢':
            self.send(message.from_user.id, '[❗]Действие отменено', reply_markup=keyboard.adminPanel)
        elif message.content_type == 'photo':
            self.send(message.from_user.id, '[✅]Рассылка успешно запущена', reply_markup=keyboard.adminPanel)
            for i in info:
                try:
                    self.bot.send_photo(chat_id=i.user_id, photo=message.json['photo'][2]['file_id'], caption=text, reply_markup=keyboard.menuUser)
                    good += 1
                except Exception as e:
                    banned += 1
            self.send(message.from_user.id,
                      f'[✅]Рассылка завершена\nОтчет\n😎Отправлено: {good}\n🤦‍Ошибки: {banned}\n🌪Общее количество: {info.count()}')
        else:
            self.send(message.from_user.id, '[✅]Рассылка успешно запущена', reply_markup=keyboard.adminPanel)
            for i in info:
                try:
                    self.send(chat_id=i.user_id, text=text, reply_markup=keyboard.menuUser)
                    good += 1
                except Exception as e:
                    banned += 1
            self.send(message.from_user.id,
                      f'[✅]Рассылка завершена\nОтчет\n😎Отправлено: {good}\n🤦‍Ошибки: {banned}\n🌪Общее количество: {info.count()}')

    @func.error_decorator
    def referalPersentOne(self, message):
        userGive = Global.select().where(Global.user_id == message.text)
        if message.text.isdigit():
            if userGive.exists():
                stepTwo = self.send(message.from_user.id, 'Введите реферальный %: ')
                self.bot.register_next_step_handler(stepTwo, self.referalPersentTwo, message.text)
            else:
                self.send(message.from_user_id, 'Пользователь не найден')
        else:
            self.send(message.from_user_id, 'Id пользователя должно состоять из цифр')

    @func.error_decorator
    def referalPersentTwo(self, message, user_id):
        if message.text.isdigit():
            Global.update(referalPersonal=int(message.text)).where(Global.user_id == user_id).execute()
            self.send(message.from_user.id, 'Успешно установлен реф процент')
        else:
            self.send(message.from_user_id, 'Реферальный % состоит из числа')

    def balanceQiwi(self):
        return f'{self.api.balance[0]}'

    @func.error_decorator
    def delBalanceFirst(self, message):
        if message.text.isdigit():
            user = Global.select().where(Global.user_id == message.text)
            if user.exists():
                addBalance = self.send(message.from_user.id,
                                       f'Баланс пользователя: {user[0].balance}\nА теперь введите сумму: ')
                self.bot.register_next_step_handler(addBalance, self.delBalanceTwo, message.text)
            else:
                self.send(message.from_user.id, '[🚫]Пользователя не существует', reply_markup=keyboard.adminPanel)
        elif message.text == '💢Отмена💢':
            self.send(message.from_user.id, '[❗]Действие отменено', reply_markup=keyboard.adminPanel)
        else:
            self.send(message.from_user.id, '[❗]Id пользователя состоит из цифр', reply_markup=keyboard.adminPanel)

    @func.error_decorator
    def delBalanceTwo(self, message, user_id):
        if message.text.isdigit():
            user = Global.select().where(Global.user_id == user_id)
            if user[0].balance >= int(message.text):
                Global.update(balance=Global.balance - int(message.text)).where(Global.user_id == user_id).execute()
                self.send(message.from_user.id, f'[✅]Вы успешно забрали {message.text} рублей у пользователя',
                          reply_markup=keyboard.adminPanel)
            else:
                self.send(message.from_user.id,
                          f'[🚫]У пользователя {user_id} не достаточно денег\nБаланс пользователя: {user[0].balance}',
                          reply_markup=keyboard.adminPanel)
        elif message.text == '💢Отмена💢':
            self.send(message.from_user.id, '[❗]Действие отменено', reply_markup=keyboard.adminPanel)
        else:
            self.send(message.from_user.id, '[❗]Сумма состоит из цифр', reply_markup=keyboard.adminPanel)

    @func.error_decorator
    def activePromoNow(self, message, c):
        infoPromo = Promo.select().where(Promo.count > 0)
        lists = ''
        for i in infoPromo:
            lists = lists + f' Промо: <pre>{i.promo}</pre>, Кол-во акт: {i.count} |'
        self.send(c.from_user.id, 'Рабочие промо\n'+lists)