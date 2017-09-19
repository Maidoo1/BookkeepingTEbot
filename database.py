import sqlite3


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