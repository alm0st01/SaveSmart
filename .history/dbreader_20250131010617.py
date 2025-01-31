import sqlite3
import eel


class DBReader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()
    
    def getattrwithattr(self, reqattr, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        query = f"SELECT {reqattr} FROM accountcreds WHERE {attr1} = ?"
        self.cursor.execute(query, (val1,))
        result = str(self.cursor.fetchone())
        return result[2:-3]
    
    def getentrywithattr(self, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        query = f"SELECT * FROM accountcreds WHERE {attr1} = ?"
        self.cursor.execute(query, (val1,))
        return list(self.cursor.fetchone())
        

    def signup(self, username, fname, lname, email, password):
        info = (username, fname, lname, email, password)
        self.cursor.execute("INSERT INTO accountcreds (username, fname, lname, email, password) VALUES (?,?,?,?,?)", info)
        self.cursor.connection.commit()

    def login(self, email, password):
        self.cursor.execute("SELECT * FROM accountcreds WHERE email = ? AND password = ?", (email, password))
        return self.cursor.fetchone()

global dbreader
dbreader = DBReader()


