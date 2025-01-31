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
        exists = self.cursor.execute("SELECT * FROM accountcreds WHERE email = ? OR username = ?", (email, username))
        if exists.fetchone() == None:
            self.cursor.execute("INSERT INTO accountcreds (username, fname, lname, email, password) VALUES (?,?,?,?,?)", info)
            self.cursor.connection.commit()
            return True
        else:
            return False


    def login(self, email, password, ret_info=False):

        self.cursor.execute("SELECT * FROM accountcreds WHERE email = ? AND password = ?", (email, password))
        user_info = self.cursor.fetchone()
        if ret_info:
            if user_info == None:
                print("FALSE")
                return False
            else:
                print("TRUE")
                return user_info
        else:
            if user_info == None:
                print("FALSE")
                return False
            else:
                print("TRUE")
                return True
    
    def get_value(self, attr):
        self.cursor.execute



dbreaderobj = DBReader()

@eel.expose
def getattrwithattr(reqattr, attr1, val1):
    return dbreaderobj.getattrwithattr(reqattr, attr1, val1)

@eel.expose
def getentrywithattr(attr1, val1):
    return dbreaderobj.getentrywithattr(attr1, val1)

@eel.expose
def login(email, password, ret_info=False):
    return dbreaderobj.login(email, password, ret_info)


@eel.expose
def signup(username, fname, lname, email, password):
    print(username, fname, lname, email, password)
    return dbreaderobj.signup(username, fname, lname, email, password)