import sqlite3
from random import randint

class DataBase:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.feedback = None

    def connect(self, db):
        self.connection = sqlite3.connect('%s.sqlite' % db)
        self.cursor = self.connection.cursor()

    def db_command(self, command):
        self.feedback = self.cursor.execute(command)
        self.connection.commit()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()


def debt_sender():
    text_dict = {
        0: 'Хэлов поц. Ты попал на бабки!\n'
           'Некто по именем {} купил {}.\n'
           'И эта параша стоила целых {} рубасов!\n'
           'Отдай ему, плес, {} рублей, братан.',

        1: 'Ну здарова.\n'
           'Тут {} купил {} за {} деревянных.\n'
           'Так что скидывай ему {}, пока не поздно.',

        2: 'Че почем?\n'
           '{} закупился парашей под названием {}.\n'
           'Знаешь сколько все это стоило? {} доллАров!\n'
           'Шутка. Кароч скинь ему {} рубликов и забудем все, что произошло.\n',

        3: 'Моё увожение!\n'
           'Господин {} изымел желание приобрести в магазине {}.\n'
           'Стоимость сего изыскания - {} Русских рублей.\n'
           'Так что убедительно прошу Вас отдать ему эти несчастные {} рублей на карту.',

        4: 'Э бля\n'
           'Я {}, я купил {} за {} рубасов, так что кидай мне на карту {} рублей, пока я тебе не уебал',

        5: 'Hello, my dear friend!\n'
           'I, fucking {}, bought the {} for {} Russian DOLLARS, so give me my money, please.\n'
           'Just {} Russian DOLLARS! Nothing more.',

        6: 'Имя: {}\n'
           'Покупка: {}\n'
           'Стоимость: {} в рублях\n'
           'Ты должен: {} в рублях',

        7: 'Недавно {} звонил твоей маме и сказал, что она купила {}.\n'
           'Эта параша стоила {} рубликов, ты можешь себе представить? У тебя есть воображение?\n'
           'Короче, скинь этому дауну {} денег на карту.',

        8: 'Не хочется тебя беспокоить, но {} дал ёбу и закупил {}.\n'
           '{} денег потратил на эту хуйню!\n'
           'Не буду томить, кинь ему {} рубасов, и закончим на этом.'
    }

    random_num = randint(0, len(text_dict)-1)
    return text_dict[random_num]
