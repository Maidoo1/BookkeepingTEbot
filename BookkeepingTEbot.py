import telebot
import sqlite3

tb_token = '428621375:AAHApm2gZZ0sdvR6PI2wce60_WDwnaYgOVw'

bot = telebot.TeleBot(tb_token)


def decorator_creator(db):
    def db_decorator(func):
        def db_connection(item):
            connection = sqlite3.connect(str(db) + '.sqlite')
            cursor = connection.cursor()
            cursor.execute(func(item))
            cursor.close()
            connection.close()

        return db_connection

    return db_decorator


@decorator_creator('purchases')
def finder(item):
    return 'SELECT * FROM purchases WHERE item LIKE "{}"'.format(item)


class Bookkeeper:
    def __init__(self):
        self.user_dict = {}
        self.user_id = None
        self.user_name = None
        self.phone = None
        self.item = None
        self.price = None

    @staticmethod
    def register_next_step(message, text, next_func):
        request = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(request, next_func)

    @staticmethod
    def deleter(item):
        conn = sqlite3.connect('purchases.sqlite')
        c = conn.cursor()
        c.execute('DELETE FROM purchases WHERE item = "{}"'.format(item))
        c.close()
        conn.close()

    def register(self):
        conn = sqlite3.connect('users.sqlite')
        c = conn.cursor()
        c.execute('INSERT INTO users VALUES ({}, "{}", "{}")'.format(self.user_id, self.user_name, self.phone))
        conn.commit()
        c.close()
        conn.close()

    def add_purchase(self):
        conn = sqlite3.connect('purchases.sqlite')
        c = conn.cursor()
        c.execute('INSERT INTO purchases VALUES("{}", "{}", "{}")'.format(self.user_name, self.item, self.price))
        conn.commit()
        c.close()
        conn.close()


user_dict = {}


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, 'Список команд:\n'
                                      '/register - Зарегистрироваться в величайшей системе человечества\n'
                                      '/add_purchase - Добавить покупку\n')


# Команда для ввода имени и номера телефона, привязанного к карте
@bot.message_handler(commands=['register'])
def register(message):
    user_dict[message.chat.id] = Bookkeeper()
    user_dict[message.chat.id].user_id = message.chat.id
    Bookkeeper.register_next_step(message, 'Какое название ты себе дашь?', add_name)


def add_name(message):
    user_dict[message.chat.id].user_name = str(message.text)
    Bookkeeper.register_next_step(message, 'Введи номер телефона, к которому привязана карта', add_phone)


def add_phone(message):
    user_dict[message.chat.id].phone = str(message.text)
    user_dict[message.chat.id].register()
    bot.send_message(message.chat.id, 'Закончено')


# Команда для добавления сделанной покупки в БД
@bot.message_handler(commands=['add_purchase'])
def add_purchase(message):
    user_dict[message.chat.id] = Bookkeeper()

    user_dict[message.chat.id].user_id = message.chat.id
    user_dict[message.chat.id].name = str(message.from_user.first_name)

    Bookkeeper.register_next_step(message, 'Что ты купил, тварь?', add_item)


def add_item(message):
    item = message.text
    user_dict[message.chat.id].item = item

    Bookkeeper.register_next_step(message, 'И сколько оно стоило?', add_price)


def add_price(message):
    price = message.text
    user_dict[message.chat.id].price = price
    user_dict[message.chat.id].add_purchase()

    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для поиска покупок в БД
@bot.message_handler(commands=['find'])
def find(message):
    Bookkeeper.register_next_step(message, 'Что ты хочешь найти?', find_anything)


def find_anything(message):
    item = str(message.text)
    finder(item)
    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для удаления покупок из БД
@bot.message_handler(commands=['delete'])
def delete(message):
    Bookkeeper.register_next_step(message, 'И что же ты захотел удалить?', deleter)


def deleter(message):
    item = str(message.text)
    Bookkeeper.deleter(item)
    bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)
