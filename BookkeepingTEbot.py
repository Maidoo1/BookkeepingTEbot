import telebot
import database

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

    def add_purchase(self):
        db = database.DataBase()

        if 'None' not in self.names:
            self.debt = int(self.price)//(len(self.names)+1)
        else:
            self.debt = int(self.price)//len(self.names)

        db.connect('purchases')
        db.db_command('INSERT INTO purchases VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
            self.user_name, self.item, self.price, self.names[0], self.debt, self.names[1], self.debt))

        try:
            [bot.send_message(i, 'Хэлов поц. Ты попал на бабки!\n'
                                 'Некто по именем {} купил {}.\n'
                                 'И эта параша стоила целых {} рубасов!\n'
                                 'Отдай ему, плес, {} рублей, братан.'.format(self.user_name, self.item, self.price,
                                                                              self.debt)) for i in self.names]
        except telebot.apihelper.ApiException:
            pass

        db.disconnect()

    def register(self):
        db = database.DataBase()
        db.connect('users')
        db.db_command('INSERT INTO users VALUES ("{}", "{}", "{}")'.format(self.user_id, self.user_name, self.phone))
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

    def finder(self):
        db = database.DataBase()
        db.connect('purchases')
        db.db_command('SELECT * FROM purchases WHERE item LIKE "{}"'.format(self.item))
        db.disconnect()

    def deleter(self):
        db = database.DataBase()
        db.connect('purchases')
        db.db_command('DELETE FROM purchases WHERE item = "{}"'.format(self.item))
        db.disconnect()

    def find_id(self, user_name):
        db = database.DataBase()
        db.connect('users')
        db.db_command('SELECT user_id FROM users WHERE name LIKE "{}"'.format(user_name))
        self.db_feedback = db.feedback
        [self.names.append(i[0]) for i in self.db_feedback]
        db.disconnect()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, 'Примеры команд:\n'
                                      '/register Король 8-800-555-35-35 - Зарегистрироваться в величайшей системе '
                                      'человечества под именем Король с номером телефона 8-800-555-35-35\n'
                                      '/purchase Вафелька 700 - Добавить покупку Вафелька ценой 700 рублей,'
                                      'деньги должны будут все соседи'
                                      '/purchase Вафелька 700 Король - Добавить покупку Вафелька ценой 700 рублей,'
                                      'деньги должен будет только Король\n')


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
        bookkeeper.find_id(string[3])
        bookkeeper.names.append('None')

    except IndexError:
        bookkeeper.other_users()

    bookkeeper.add_purchase()
    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для поиска покупок в БД
@bot.message_handler(commands=['find'])
def find(message):
    string = str(message.text).split()

    bookkeeper = Bookkeeper()

    bookkeeper.item = string[1]

    bookkeeper.finder()
    bot.send_message(message.chat.id, 'Закончено')


# Тестовая команда для удаления покупок из БД
@bot.message_handler(commands=['delete'])
def delete(message):
    string = str(message.text).split()

    bookkeeper = Bookkeeper()

    bookkeeper.item = string[1]

    bookkeeper.deleter()
    bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)