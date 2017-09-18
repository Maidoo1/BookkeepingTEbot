import telebot
import database
import json


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

    @staticmethod
    def register_next_step(message, text, next_func):
        request = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(request, next_func)

    @staticmethod
    def send_message(text):
        with open('texts.json', 'r', encoding='utf-8') as json_file:
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
            answer = database.debt_sender()
            [bot.send_message(i, answer.format(self.user_name, self.item, self.price, self.debt)) for i in self.names]

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
        db.db_command('SELECT name FROM users WHERE user_id LIKE "{}"'.format(self.user_id))
        self.db_feedback = [i for i in db.feedback]
        self.user_name = self.db_feedback[0][0]
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
        db.disconnect()

    # Not ready for using
    def deleter(self):
        db = database.DataBase()
        db.connect('purchases')
        db.db_command('DELETE FROM purchases WHERE item = "{}"'.format(self.item))
        db.disconnect()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, Bookkeeper.send_message('start'))


@bot.message_handler(commands=['test'])
def test(message):
    bookkeeper = Bookkeeper()
    bookkeeper.user_id = message.chat.id
    bookkeeper.other_users()


# Команда для ввода имени и номера телефона, привязанного к карте
@bot.message_handler(commands=['register', 'регистрация'])
def register(message):
    string = (str(message.text)).split()

    bookkeeper = Bookkeeper()

    bookkeeper.user_id = message.chat.id
    bookkeeper.user_name = string[1]
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
    bookkeeper.item = string[1]
    bookkeeper.price = string[2]

    try:
        user_name = string[3]
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

    string = 'Вот те список пацанов с номерами:\n'
    for i in bookkeeper.db_feedback:
        string += '• ' + i[0] + ' - ' + i[1] + '\n'

    bot.send_message(message.chat.id, string)


# Тестовая команда для удаления покупок из БД
@bot.message_handler(commands=['delete', 'прощаю'])
def delete(message):
    string = str(message.text).split()

    bookkeeper = Bookkeeper()

    bookkeeper.item = string[1]

    bookkeeper.deleter()
    bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)