import telebot
import sqlite3

tb_token = '428621375:AAHApm2gZZ0sdvR6PI2wce60_WDwnaYgOVw'

bot = telebot.TeleBot(tb_token)


# @bot.message_handler(content_types='text')
# def start(message):
#     bot.send_message(message.chat.id, message.text)

class Bookkeeper:
    def __init__(self):
        self.user_dict = {}
        self.user_id = None
        self.name = None
        self.item = None
        self.price = None

    @staticmethod
    def register(id, name, phone):
        # reg_dict = {id: [name, phone]}
        #
        # with open('users.txt', 'a') as file:
        #         file.write(str(reg_dict) + '\n')
        conn = sqlite3.connect('users.sqlite')
        c = conn.cursor()
        # c.execute('''CREATE TABLE users (id int auto_increment primary key,name varchar, password varchar)''')
        c.execute("INSERT INTO users (user_id, name, phone) VALUES ({},{},{})".format(id, name, phone))
        conn.commit()
        c.close()
        conn.close()

    def add_purchase(self):
        self.user_dict[self.user_id] = [self.name, self.item, self.price]

        with open('bd.txt', 'a') as file:
            file.write(str(self.user_dict) + '\n')


global_dict = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Список команд:\n'
                                      '/register - Зарегистрироваться в величайшей системе человечества\n'
                                      '/add_purchase - Добавить покупку\n')


@bot.message_handler(commands=['register'])
def register(message):
    request = bot.send_message(message.chat.id, 'Какое название ты себе дашь?')
    bot.register_next_step_handler(request, add_name)


def add_name(message):
    global name
    name = str(message.text)
    request = bot.send_message(message.chat.id, 'Введи номер телефона, к которому привязана карта')
    bot.register_next_step_handler(request, add_phone)


def add_phone(message):
    phone = str(message.text)
    Bookkeeper.register(str(message.chat.id), str(name), str(phone))
    bot.send_message(message.chat.id, 'Закончено')


@bot.message_handler(commands=['add_purchase'])
def add_purchase(message):
    global_dict[message.chat.id] = Bookkeeper()

    global_dict[message.chat.id].user_id = str(message.chat.id)
    global_dict[message.chat.id].name = str(message.from_user.first_name)

    request = bot.send_message(message.chat.id, 'Что ты купил, тварь?')
    bot.register_next_step_handler(request, add_item)


def add_item(message):
    item = message.text
    global_dict[message.chat.id].item = str(item)

    request = bot.send_message(message.chat.id, 'И сколько оно стоило?')
    bot.register_next_step_handler(request, add_price)


def add_price(message):
    price = message.text
    global_dict[message.chat.id].price = str(price)
    global_dict[message.chat.id].add_purchase()

    bot.send_message(message.chat.id, 'Закончено')


if __name__ == '__main__':
    bot.polling(none_stop=True)
