import telebot
import database

tb_token = '428621375:AAHApm2gZZ0sdvR6PI2wce60_WDwnaYgOVw'

bot = telebot.TeleBot(tb_token)


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
        self.db_feedback = None

    @staticmethod
    def register_next_step(message, text, next_func):
        request = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(request, next_func)

    # @decorator_creator('users')
    # def is_register_command(self):
    #     return 'SELECT name FROM users WHERE user_id LIKE "{}"'.format(self.user_id)
    #
    # def is_register(self):
    #     self.is_register_command()
    #     self.names.append(self.db_feedback[0][0])
    #
    # @decorator_creator('users')
    # def other_users_command(self):
    #     return 'SELECT user_id FROM users WHERE user_id NOT LIKE "{}"'.format(self.user_id)
    #
    def other_users(self):
        # self.other_users_command()
        # users = [i[0] for i in self.db_feedback]
        # for i in users:
        #     self.user_id = i
        #     self.is_register()
        db = database.DataBase()
        db.connect('users')
        db.command = 'SELECT user_id FROM users WHERE user_id NOT LIKE "{}"'.format(self.user_id)
        db.db_command()
        self.db_feedback = db.feedback
        print([i for i in self.db_feedback])
        db.disconnect()
    #
    # @decorator_creator('purchases')
    # def finder(self):
    #     return 'SELECT * FROM purchases WHERE item LIKE "{}"'.format(self.item)
    #
    # @decorator_creator('purchases')
    # def deleter(self):
    #     return 'DELETE FROM purchases WHERE item = "{}"'.format(self.item)
    #
    # @decorator_creator('users')
    # def register(self):
    #     return 'INSERT INTO users VALUES ({}, "{}", "{}")'.format(self.user_id, self.user_name, self.phone)
    #
    # @decorator_creator('purchases')
    # def add_purchase(self):
    #     return 'INSERT INTO purchases VALUES("{}", "{}", "{}", "{}", "{}")'.format(
    #         self.names[0], self.item, self.price, self.names[1], self.names[2])
    #
    # @decorator_creator('users')
    # def find_id(self):
    #     return 'SELECT user_id FROM users WHERE name LIKE "{}"'.format(self.user_name)
    #
    # def purchase(self):
    #     self.add_purchase()
    #     for i in self.names[1:]:
    #         self.user_name = i
    #         self.find_id()
    #         try:
    #             bot.send_message(self.db_feedback[0][0], 'Теперь ты должен бабло персонажу под именем: {}, в размере {}'
    #                                                  ' рублей, потому что он купил {}'.format(self.names[0],
    #                                                   int(self.price)//(len(self.names)-1), self.item))
    #         except IndexError:
    #             pass


# @bot.message_handler(commands=['start', 'help'])
# def start(message):
#     bot.send_message(message.chat.id, 'Примеры команд:\n'
#                                       '/register Король 8-800-555-35-35 - Зарегистрироваться в величайшей системе '
#                                       'человечества под именем Король с номером телефона 8-800-555-35-35\n'
#                                       '/purchase Вафелька 700 - Добавить покупку Вафелька ценой 700 рублей,'
#                                       'деньги должны будут все соседи'
#                                       '/purchase Вафелька 700 Король - Добавить покупку Вафелька ценой 700 рублей,'
#                                       'деньги должен будет только Король\n')
#
#
@bot.message_handler(commands=['test'])
def test(message):
    bookkeeper = Bookkeeper()
    bookkeeper.user_id = message.chat.id
    bookkeeper.other_users()
#
#
# # Команда для ввода имени и номера телефона, привязанного к карте
# @bot.message_handler(commands=['register', 'регистрация'])
# def register(message):
#     string = (str(message.text)).split()
#
#     bookkeeper = Bookkeeper()
#
#     bookkeeper.user_id = message.chat.id
#     bookkeeper.user_name = string[1]
#     bookkeeper.phone = string[2]
#
#     bookkeeper.register()
#     bot.send_message(message.chat.id, 'Закончено')
#
#
# # Команда для добавления сделанной покупки в БД
# @bot.message_handler(commands=['purchase', 'покупка'])
# def add_purchase(message):
#     string = str(message.text).split()
#
#     bookkeeper = Bookkeeper()
#
#     bookkeeper.user_id = message.chat.id
#     bookkeeper.is_register()
#     bookkeeper.item = string[1]
#     bookkeeper.price = string[2]
#
#     try:
#         bookkeeper.names.append(string[3])
#         bookkeeper.names.append('None')
#
#     except IndexError:
#         bookkeeper.other_users()
#
#     bookkeeper.purchase()
#     bot.send_message(message.chat.id, 'Закончено')
#
#
# # Тестовая команда для поиска покупок в БД
# @bot.message_handler(commands=['find'])
# def find(message):
#     string = str(message.text).split()
#
#     bookkeeper = Bookkeeper()
#
#     bookkeeper.item = string[1]
#
#     bookkeeper.finder()
#     bot.send_message(message.chat.id, 'Закончено')
#
#
# # Тестовая команда для удаления покупок из БД
# @bot.message_handler(commands=['delete'])
# def delete(message):
#     string = str(message.text).split()
#
#     bookkeeper = Bookkeeper()
#
#     bookkeeper.item = string[1]
#
#     bookkeeper.deleter()
#     bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)