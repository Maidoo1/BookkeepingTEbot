import telebot
import sqlite3

tb_token = '428621375:AAHApm2gZZ0sdvR6PI2wce60_WDwnaYgOVw'

bot = telebot.TeleBot(tb_token)


def decorator_creator(db):
    def db_decorator(func):
        def db_connection(self):
            connection = sqlite3.connect('%s.sqlite' % db)
            cursor = connection.cursor()

            cursor.execute(func(self))
            connection.commit()

            cursor.close()
            connection.close()

        return db_connection
    return db_decorator


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

    @decorator_creator('purchases')
    def finder(self):
        return 'SELECT * FROM purchases WHERE item LIKE "{}"'.format(self.item)

    @decorator_creator('purchases')
    def deleter(self):
        return 'DELETE FROM purchases WHERE item = "{}"'.format(self.item)

    @decorator_creator('users')
    def register(self):
        return 'INSERT INTO users VALUES ({}, "{}", "{}")'.format(self.user_id, self.user_name, self.phone)

    @decorator_creator('purchases')
    def add_purchase(self):
        return 'INSERT INTO purchases VALUES("{}", "{}", "{}")'.format(self.user_name, self.item, self.price)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, 'Список команд:\n'
                                      '/register - Зарегистрироваться в величайшей системе человечества\n'
                                      '/add_purchase - Добавить покупку\n')


# Команда для ввода имени и номера телефона, привязанного к карте
@bot.message_handler(commands=['register'])
def register(message):
    bookkeeper = Bookkeeper()

    string = (str(message.text)).split()

    bookkeeper.user_id = message.chat.id
    bookkeeper.user_name = string[1]
    bookkeeper.phone = string[2]

    bookkeeper.register()
    bot.send_message(message.chat.id, 'Закончено')


# Команда для добавления сделанной покупки в БД
@bot.message_handler(commands=['add_purchase'])
def add_purchase(message):
    bookkeeper = Bookkeeper()

    string = str(message.text).split()

    bookkeeper.user_id = message.chat.id
    bookkeeper.user_name = str(message.from_user.first_name)
    bookkeeper.item = string[1]
    bookkeeper.price = string[2]

    bookkeeper.add_purchase()
    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для поиска покупок в БД
@bot.message_handler(commands=['find'])
def find(message):
    bookkeeper = Bookkeeper()

    string = str(message.text).split()

    bookkeeper.item = string[1]

    bookkeeper.finder()
    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для удаления покупок из БД
@bot.message_handler(commands=['delete'])
def delete(message):
    bookkeeper = Bookkeeper()

    string = str(message.text).split()

    bookkeeper.item = string[1]

    bookkeeper.deleter()
    bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)