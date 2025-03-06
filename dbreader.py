import sqlite3
import eel
from random import randint

from encrypt import encrypt

enc: encrypt = encrypt()


class account_reader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()
        self.encrypt = enc
    
    def get_attr_with_attr(self, reqattr, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        #attr1 = self.encrypt.encrypt_text(attr1)
        val1 = self.encrypt.encrypt_text(val1)
        #reqattr = self.encrypt.encrypt_text(reqattr)
        query = f"SELECT {reqattr} FROM accountcreds WHERE {attr1} = ?"
        self.cursor.execute(query, (val1,))
        result = str(self.cursor.fetchone())

        return self.encrypt.decrypt_text(result)

    def get_acc_id_with_attr(self, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        try:
            val1 = self.encrypt.encrypt_text(val1)
            self.cursor.execute("SELECT account_id FROM accountcreds WHERE email = ?", (val1,))
            result = self.cursor.fetchone()
            
            if result is None:
                print(f"No account found for email={val1}")
                return None
                
            account_id = result[0]
            print(f"Found account_id: {account_id}")
            
            if isinstance(account_id, bytes):
                return self.encrypt.decrypt_text(account_id)
            return account_id
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def getentrywithattr(self, attr1, val1):
        # Only use the function if the username or email are given 
        # as these are the only unique user credentials
        #attr1 = self.encrypt.encrypt_text(attr1)
        val1 = self.encrypt.encrypt_text(val1)
        query = f"SELECT * FROM accountcreds WHERE {attr1} = ?"
        self.cursor.execute(query, (val1,))
        result = list(self.cursor.fetchone())

        decrypted_result = []
        for i, value in enumerate(result):
            decrypted_result.append(self.encrypt.decrypt_text(value))

        return decrypted_result
        

    def signup(self, username, fname, lname, email, password):
        enc_username = self.encrypt.encrypt_text(username)
        enc_fname = self.encrypt.encrypt_text(fname)
        enc_lname = self.encrypt.encrypt_text(lname)
        enc_email = self.encrypt.encrypt_text(email)
        enc_password = self.encrypt.encrypt_text(password)

        account_id = str(randint(10**8, (10**9)-1))
        enc_account_id = self.encrypt.encrypt_text(account_id)

        info = (enc_account_id, enc_username, enc_fname, enc_lname, enc_email, enc_password)
        exists = self.cursor.execute("SELECT * FROM accountcreds WHERE email = ? OR username = ?", (enc_email, enc_username))
        acc_id_exists = self.cursor.execute("SELECT * FROM accountcreds WHERE account_id = ?", (enc_account_id,))
        acc_id_exists_bool = acc_id_exists.fetchone()
        if exists.fetchone() == None and acc_id_exists_bool == None:
            self.cursor.execute("INSERT INTO accountcreds (account_id, username, fname, lname, email, password) VALUES (?,?,?,?,?,?)", info)
            self.cursor.connection.commit()
            return True
        else:
            if acc_id_exists_bool:
                self.signup(username, fname, lname, email, password)
            else:
                return False


    def login(self, email, password, ret_info=False):
        email = self.encrypt.encrypt_text(email)
        password = self.encrypt.encrypt_text(password)


        self.cursor.execute("SELECT * FROM accountcreds WHERE email = ? AND password = ?", (email, password))
        user_info = self.cursor.fetchone()
        # temporarily, ret_info should equal false until the decryption process is complete
        if ret_info:
            if user_info == None:
                print("FALSE A")
                return False
            else:
                print("TRUE A")
                return user_info
        else:
            if user_info == None:
                print("FALSE B")
                return False
            else:
                print("TRUE B")
                return True

class transaction_reader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()
        self.ar = account_reader()
        self.encrypt = enc
    
    def get_attr_with_id(self, transaction_id, reqattr):
        transaction_id = self.encrypt.encrypt_text(transaction_id)
        #reqattr = self.encrypt.encrypt_text(reqattr)
        # This function should only be used with a transaction ID
        query = f"SELECT {reqattr} FROM transactions WHERE transaction_id = ?"
        self.cursor.execute(query, (transaction_id,))
        result = str(self.cursor.fetchone())
        result = result[2:-3]
        result = self.encrypt.decrypt_text(result)
        print(result)
        return result
    
    def get_latest_balance(self, account_id):
        account_id = self.encrypt.encrypt_text(account_id)
        self.cursor.execute(f'''
                            SELECT balance_after FROM transactions WHERE account_id = ?
                            ORDER BY transaction_date DESC, transaction_id DESC 
                            LIMIT 1
                            ''', (account_id,))
        
        result = self.cursor.fetchone()
        if result:
            return float(self.encrypt.encrypt_text(result[0]))
        else:
            return 0.0 # If the user has made no transactions, this will return

    def add_transaction(self, transaction_type, amount, transaction_date, name, description):
        account_id = self.ar.get_acc_id_with_attr('email', self.encrypt.encrypt_text(eel.get_cookie('email')()))
        latest_balance = self.get_latest_balance(account_id)
        new_balance = latest_balance
        amt = float(amount)


        if account_id is None:
            print("Error: Could not find account ID")
            return False
        print(f"Using account_id: {account_id}")
        
        if transaction_type == "Deposit":
            new_balance += amt
        elif transaction_type == "Withdrawal" or transaction_type == "Transfer":
            new_balance -= amt

        transaction_type = self.encrypt.encrypt_text(transaction_type)
        amt = self.encrypt.encrypt_text(amount)
        transaction_date = self.encrypt.encrypt_text(transaction_date)
        name = self.encrypt.encrypt_text(name)
        description = self.encrypt.encrypt_text(description)
        new_balance_str = self.encrypt.encrypt_text(new_balance)
        
        self.cursor.execute(f'INSERT INTO transactions (account_id, transaction_type, amount, transaction_date, transaction_name, description, balance_after) VALUES (?,?,?,?,?,?,?)', (account_id, transaction_type, amt, transaction_date, name, description, new_balance_str))
        self.cursor.connection.commit()
        return True
    
    def get_transactions(self, account_id, limit=5, offset=0):
        account_id = self.encrypt.encrypt_text(account_id)

        self.cursor.execute('''
            SELECT transaction_id, transaction_type, amount, transaction_date, transaction_name, description 
            FROM transactions 
            WHERE account_id = ? 
            ORDER BY transaction_date DESC, transaction_id DESC
            LIMIT ? OFFSET ?
        ''', (account_id, limit, offset))

        result = self.cursor.fetchall()
        
        decrypted_result = []
        for i, value in enumerate(result):
            for x, valuex in enumerate(value):
                decrypted_result.append(self.encrypt.decrypt_text(valuex))

        return decrypted_result
    
    def get_account_transactions_by_category(self, account_id, category, limit=5, offset=0):
        account_id = self.encrypt.encrypt_text(account_id)
        #category = self.encrypt.encrypt_text(category)

        self.cursor.execute('''
            SELECT transaction_id, transaction_type, amount, transaction_date, transaction_name, description 
            FROM transactions 
            WHERE account_id = ? AND transaction_name = ?
            ORDER BY transaction_date DESC, transaction_id DESC
            LIMIT ? OFFSET ?
        ''', (account_id, category, limit, offset))

        result = self.cursor.fetchall()
        
        decrypted_result = []
        for i, value in enumerate(result):
            for x, valuex in enumerate(value):
                decrypted_result.append(self.encrypt.decrypt_text(valuex))

        return decrypted_result

    def get_transaction_count(self, account_id):
        account_id = self.encrypt.encrypt_text(account_id)
        self.cursor.execute('SELECT COUNT(*) FROM transactions WHERE account_id = ?', (account_id,))
        return self.cursor.fetchone()[0]
    
    def get_category_percentages(self, account_id):
        account_id = self.encrypt.encrypt_text(account_id)

        self.cursor.execute('''
            SELECT transaction_name, COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE account_id = ?), 2) as percentage
            FROM transactions 
            WHERE account_id = ?
            GROUP BY transaction_name
            ORDER BY count DESC
        ''', (account_id, account_id))
        
        result = self.cursor.fetchall()
        
        decrypted_result = []
        for i, value in enumerate(result):
                decrypted_category = self.encrypt.decrypt_text(value[0])
                decrypted_result.append((decrypted_category, value[1], value[2]))

        return decrypted_result
    
    def get_category_(self, account_id):
        self.cursor.execute('''
            SELECT transaction_name, COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions WHERE account_id = ?), 2) as percentage
            FROM transactions 
            WHERE account_id = ?
            GROUP BY transaction_name
            ORDER BY count DESC
        ''', (account_id, account_id))
        return self.cursor.fetchall()

        

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
def get_account_transactions_by_category(category, limit=5, offset=0):
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_account_transactions_by_category(account_id, category, limit, offset)

@eel.expose
def get_latest_balance():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_latest_balance(account_id)

@eel.expose
def get_transaction_count():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_transaction_count(account_id)

@eel.expose
def get_category_values():
    mode = 1

    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    if mode == 1: # return percentages
        return tr.get_category_percentages(account_id)
    #elif mode == 2:
    #    return tr.