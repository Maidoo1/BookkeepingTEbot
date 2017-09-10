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
    user_dict[message.chat.id].user_name = str(message.from_user.first_name)

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
    user_dict[message.chat.id] = Bookkeeper()
    Bookkeeper.register_next_step(message, 'Что ты хочешь найти?', find_anything)


def find_anything(message):
    user_dict[message.chat.id].item = str(message.text)
    user_dict[message.chat.id].finder()
    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для удаления покупок из БД
@bot.message_handler(commands=['delete'])
def delete(message):
    user_dict[message.chat.id] = Bookkeeper()
    Bookkeeper.register_next_step(message, 'И что же ты захотел удалить?', deleter)


def deleter(message):
    user_dict[message.chat.id].item = str(message.text)
    user_dict[message.chat.id].deleter()
    bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)