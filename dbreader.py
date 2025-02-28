import sqlite3
import eel


class account_reader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()
    
    def get_attr_with_attr(self, reqattr, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        query = f"SELECT {reqattr} FROM accountcreds WHERE {attr1} = ?"
        self.cursor.execute(query, (val1,))
        result = str(self.cursor.fetchone())

        return result[2:-3]
    
    def get_acc_id_with_attr(self, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        query = f"SELECT account_id FROM accountcreds WHERE {attr1} = ?"
        self.cursor.execute(query, (val1,))
        result = str(self.cursor.fetchone())

        print(result) #temp
        print(result[1]) #temp
        return int(result[1])
    
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

class transaction_reader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()
        self.ar = account_reader()
    
    def get_attr_with_id(self, transaction_id, reqattr):
        # This function should only be used with a transaction ID
        query = f"SELECT {reqattr} FROM transactions WHERE transaction_id = ?"
        self.cursor.execute(query, (transaction_id,))
        result = str(self.cursor.fetchone())
        return result[2:-3]
    
    def get_latest_balance(self, account_id):
        self.cursor.execute(f'''
                            SELECT balance_after FROM transactions WHERE account_id = ?
                            ORDER BY transaction_date DESC, transaction_id DESC 
                            LIMIT 1
                            ''', (account_id,))
        
        result = self.cursor.fetchone()
        if result:
            return float(result[0])
        else:
            return 0.0 # If the user has made no transactions, this will return

    def add_transaction(self, transaction_type, amount, transaction_date, name, description):
        account_id = self.ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
        latest_balance = self.get_latest_balance(account_id)
        new_balance = latest_balance
        amt = float(amount)
        
        if transaction_type == "Deposit":
            new_balance += amt
        elif transaction_type == "Withdrawal" or transaction_type == "Transfer":
            new_balance -= amt

        self.cursor.execute(f'INSERT INTO transactions (account_id, transaction_type, amount, transaction_date, transaction_name, description, balance_after) VALUES (?,?,?,?,?,?,?)', (account_id, transaction_type, amt, transaction_date, name, description, new_balance))
        self.cursor.connection.commit()
        return True
    
    def get_transactions(self, account_id, limit=5, offset=0):
        self.cursor.execute('''
            SELECT transaction_id, transaction_type, amount, transaction_date, transaction_name, description 
            FROM transactions 
            WHERE account_id = ? 
            ORDER BY transaction_date DESC, transaction_id DESC
            LIMIT ? OFFSET ?
        ''', (account_id, limit, offset))
        return self.cursor.fetchall()

    def get_transaction_count(self, account_id):
        self.cursor.execute('SELECT COUNT(*) FROM transactions WHERE account_id = ?', (account_id,))
        return self.cursor.fetchone()[0]

        

ar = account_reader()
tr = transaction_reader()

@eel.expose
def getattrwithattr(reqattr, attr1, val1):
    return ar.get_attr_with_attr(reqattr, attr1, val1)

@eel.expose
def getentrywithattr(attr1, val1):
    return ar.getentrywithattr(attr1, val1)

@eel.expose
def login(email, password, ret_info=False):
    return ar.login(email, password, ret_info)


@eel.expose
def signup(username, fname, lname, email, password):
    #print(username, fname, lname, email, password) #temp
    return ar.signup(username, fname, lname, email, password)

@eel.expose
def add_transaction(transaction_type, amount, transaction_date, name, description):
    return tr.add_transaction(transaction_type, amount, transaction_date, name, description)

@eel.expose
def get_account_transactions(limit=5, offset=0):
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_transactions(account_id, limit, offset)

@eel.expose
def get_latest_balance():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_latest_balance(account_id)

@eel.expose
def get_transaction_count():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_transaction_count(account_id)