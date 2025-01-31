import sqlite3
import eel


class DBReader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()

    def signup(self, username, fname, lname, email, password):
        info = (username, fname, lname, email, password)
        self.cursor.execute("INSERT INTO accountcreds (username, fname, lname, email, password) VALUES (?,?,?,?,?)", info)
        self.cursor.connection.commit()

    def login(self, email, password):
        self.cursor.execute("SELECT * FROM accountcreds WHERE email = ? AND password = ?", (email, password))
        return self.cursor.fetchone()

global dbreader
dbreader = DBReader()


