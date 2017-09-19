import telebot
import database
import json
from random import randint


tb_token = '428621375:AAHApm2gZZ0sdvR6PI2wce60_WDwnaYgOVw'

bot = telebot.TeleBot(tb_token)

#RIP
# def decorator_creator(db):
#     def db_decorator(func):
#         def db_connection(self):
#             connection = sqlite3.connect('%s.sqlite' % db)
#             cursor = connection.cursor()
#
#             db_command = cursor.execute(func(self))
#             self.db_feedback = [i for i in db_command]
#
#             connection.commit()
#
#             cursor.close()
#             connection.close()
#
#         return db_connection
#     return db_decorator


class Bookkeeper:
    def __init__(self):
        self.user_id = None
        self.user_name = None
        self.phone = None
        self.item = None
        self.price = None
        self.names = []
        self.debt = None
        self.db_feedback = None
        self.people = ''
        self.debt_string = ''

    @staticmethod
    def register_next_step(message, text, next_func):
        request = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(request, next_func)

    @staticmethod
    def send_message(text):
        with open('text.json', 'r', encoding='utf-8') as json_file:
            file = json.load(json_file)
            return file[text]

    def add_purchase(self):
        self.debt = int(self.price)//(len(self.names)+1)

        db = database.DataBase()
        db.connect('purchases')

        for i in self.names:
            db.db_command('INSERT INTO purchases VALUES ("{}", "{}", "{}", "{}", "{}")'.format(
                self.user_name, self.item, self.price, i, self.debt))

        try:
            answer = Bookkeeper.send_message('collector')
            random_num = str(randint(0, len(answer)-1))

            [bot.send_message(i, answer[random_num].format(
                self.user_name, self.item, self.price, self.debt)) for i in self.names]

            [bot.send_message(i, Bookkeeper.send_message('table').format(
                self.user_name, self.item, self.price, self.debt, self.phone)) for i in self.names]

        except telebot.apihelper.ApiException:
            pass

        db.disconnect()

    def find_id(self, user_name):
        db = database.DataBase()
        db.connect('users')
        db.db_command('SELECT user_id FROM users WHERE name LIKE "{}"'.format(user_name))
        self.db_feedback = db.feedback
        [self.names.append(i[0]) for i in self.db_feedback]
        db.disconnect()

    def is_register(self):
        db = database.DataBase()
        db.connect('users')
        db.db_command('SELECT name, phone FROM users WHERE user_id LIKE "{}"'.format(self.user_id))
        self.db_feedback = [i for i in db.feedback]
        self.user_name = self.db_feedback[0][0]
        self.phone = self.db_feedback[0][1]
        db.disconnect()

    def other_users(self):
        db = database.DataBase()
        db.connect('users')
        db.db_command('SELECT user_id FROM users WHERE user_id NOT LIKE "{}"'.format(self.user_id))
        self.db_feedback = db.feedback
        [self.names.append(i[0]) for i in self.db_feedback]
        db.disconnect()

    def register(self):
        db = database.DataBase()
        db.connect('users')
        db.db_command('INSERT INTO users VALUES ("{}", "{}", "{}")'.format(self.user_id, self.user_name, self.phone))
        db.disconnect()

    def finder(self):
        db = database.DataBase()
        db.connect('users')
        db.db_command('SELECT name, phone FROM users WHERE user_id NOT LIKE "{}"'.format(self.user_id))

        self.db_feedback = [i for i in db.feedback]
        for i in self.db_feedback:
            self.people += '• {} - {}\n'.format(i[0], i[1])

        db.disconnect()

    def deleter(self):
        db = database.DataBase()
        db.connect('purchases')
        for i in self.names:
            db.db_command('DELETE FROM purchases WHERE item = "{}" AND debtor_id = "{}"'.format(self.item, i))
        db.disconnect()

    def debts(self):
        db = database.DataBase()
        db.connect('purchases')
        db.db_command('SELECT name, item, debt FROM purchases WHERE debtor_id LIKE "{}"'.format(self.user_id))
        self.db_feedback = [i for i in db.feedback]

        for i in self.db_feedback:
            self.debt_string += 'Имя: {}\nПокупка: {}\nТы должен: {} рублеков\n\n'.format(i[0], i[1], i[2])

        db.disconnect()


@bot.message_handler(commands=['start'])
def start(message):
    bookkeeper = Bookkeeper()
    bookkeeper.user_id = message.chat.id

    bookkeeper.finder()

    bot.send_message(message.chat.id, Bookkeeper.send_message('start'), parse_mode='HTML')
    bot.send_message(message.chat.id, bookkeeper.people, parse_mode='HTML')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, Bookkeeper.send_message('help'), parse_mode='HTML')


@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, '<b>test</b>', parse_mode='HTML')


# Команда для ввода имени и номера телефона, привязанного к карте
@bot.message_handler(commands=['register', 'регистрация'])
def register(message):
    string = (str(message.text)).split()

    bookkeeper = Bookkeeper()

    bookkeeper.user_id = message.chat.id
    bookkeeper.user_name = string[1].capitalize()
    bookkeeper.phone = string[2]

    bookkeeper.register()
    bot.send_message(message.chat.id, 'Закончено')


# Команда для добавления сделанной покупки в БД
@bot.message_handler(commands=['purchase', 'покупка'])
def add_purchase(message):
    string = str(message.text).split()

    bookkeeper = Bookkeeper()

    bookkeeper.user_id = message.chat.id
    bookkeeper.is_register()

    bookkeeper.item = string[1].capitalize()
    bookkeeper.price = string[2]

    try:
        user_name = string[3].capitalize()
        bookkeeper.find_id(user_name)

    except IndexError:
        bookkeeper.other_users()

    bookkeeper.add_purchase()
    bot.send_message(message.chat.id, 'Закончено')


# Команда для поиска людей в БД
@bot.message_handler(commands=['people', 'пацаны'])
def find(message):
    bookkeeper = Bookkeeper()
    bookkeeper.user_id = message.chat.id

    bookkeeper.finder()

    string = 'Вот те список пацанов с номерами:\n' + bookkeeper.people

    bot.send_message(message.chat.id, string, parse_mode='HTML')


# Команда для удаления покупок из БД
@bot.message_handler(commands=['delete', 'прощаю'])
def delete(message):
    string = str(message.text).split()

    bookkeeper = Bookkeeper()

    bookkeeper.user_id = message.chat.id
    bookkeeper.is_register()

    bookkeeper.item = string[1].capitalize()

    try:
        user_name = string[2].capitalize()
        bookkeeper.find_id(user_name)

    except IndexError:
        bookkeeper.other_users()

    bookkeeper.deleter()
    bot.send_message(message.chat.id, 'Закончено')


@bot.message_handler(commands=['debts', 'долги'])
def debts(message):
    bookkeeper = Bookkeeper()
    bookkeeper.user_id = message.chat.id

    bookkeeper.debts()

    bot.send_message(message.chat.id, bookkeeper.debt_string, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling(none_stop=True)