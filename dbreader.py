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
        try:
            if not val1:
                print("No value provided for lookup")
                return None
            
            # Get all users and compare decrypted values for email
            self.cursor.execute("SELECT * FROM accountcreds")
            all_users = self.cursor.fetchall()
            
            for user in all_users:
                stored_email = self.encrypt.decrypt_text(user[4])  # email at index 4
                if val1 == stored_email:
                    account_id = user[0]  # account_id at index 0
                    # Return the encrypted account_id directly
                    return account_id
                
            print(f"No account found for email={val1}")
            return None
            
        except Exception as e:
            print(f"Error in get_acc_id_with_attr: {str(e)}")
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
        try:
            # Encrypt values for database storage
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
            exists_result = exists.fetchone()

            if exists_result is None and acc_id_exists_bool is None:
                self.cursor.execute("INSERT INTO accountcreds (account_id, username, fname, lname, email, password) VALUES (?,?,?,?,?,?)", info)
                self.cursor.connection.commit()
                return {
                    'success': True,
                    'values': {
                        'username': username,  # Return original unencrypted values
                        'fname': fname,
                        'lname': lname,
                        'email': email,
                        'password': password
                    }
                }
            else:
                if acc_id_exists_bool:
                    # If only the account_id exists, try again with a new account_id
                    return self.signup(username, fname, lname, email, password)
                else:
                    # If username or email exists
                    return {'success': False}
                    
        except Exception as e:
            print(f"Error in signup: {str(e)}")
            return {'success': False}


    def login(self, email, password, ret_info=False):
        try:
            # Get all users and compare decrypted values
            self.cursor.execute("SELECT * FROM accountcreds")
            all_users = self.cursor.fetchall()
            
            for user in all_users:
                # Decrypt the stored email and password
                stored_email = self.encrypt.decrypt_text(user[4])  # email at index 4
                stored_password = self.encrypt.decrypt_text(user[5])  # password at index 5
                
                if email == stored_email and password == stored_password:
                    if ret_info:
                        # Return decrypted values for cookies
                        return {
                            'success': True,
                            'values': {
                                'username': self.encrypt.decrypt_text(user[1]),  # username
                                'fname': self.encrypt.decrypt_text(user[2]),     # fname
                                'lname': self.encrypt.decrypt_text(user[3]),     # lname
                                'email': email,                                  # use original email
                                'password': password                             # use original password
                            }
                        }
                    return True
            
            return False
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

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
        try:
            # account_id is already encrypted
            self.cursor.execute('''
                            SELECT balance_after FROM transactions WHERE account_id = ?
                            ORDER BY transaction_date DESC, transaction_id DESC 
                            LIMIT 1
                            ''', (account_id,))
            
            result = self.cursor.fetchone()
            if result and result[0]:
                decrypted_balance = self.encrypt.decrypt_text(result[0])
                print(f"Latest balance found: {decrypted_balance}")
                return float(decrypted_balance)
            return 0.0
        except Exception as e:
            print(f"Error getting balance: {str(e)}")
            return 0.0

    def add_transaction(self, transaction_type, amount, transaction_date, name, description):
        try:
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False
                
            latest_balance = self.get_latest_balance(account_id)
            new_balance = latest_balance
            amt = float(amount)

            if transaction_type == "Deposit":
                new_balance += amt
            elif transaction_type == "Withdrawal" or transaction_type == "Transfer":
                new_balance -= amt


            transaction_id = str(randint(10**8, (10**9)-1))

            # Encrypt all values for storage
            enc_transaction_type = self.encrypt.encrypt_text(transaction_type)
            enc_amount = self.encrypt.encrypt_text(str(amount))
            enc_transaction_date = self.encrypt.encrypt_text(transaction_date)
            enc_name = self.encrypt.encrypt_text(name)
            enc_description = self.encrypt.encrypt_text(description)
            enc_new_balance = self.encrypt.encrypt_text(str(new_balance))
            enc_transaction_id = self.encrypt.encrypt_text(transaction_id)
            # Don't re-encrypt account_id since it's already encrypted

            transact_id_query = self.cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (enc_transaction_id,))
            transact_id_exists = transact_id_query.fetchone()

            if transact_id_exists:
                self.add_transaction(transaction_type, amount, transaction_date, name, description)
            
            self.cursor.execute('''
                INSERT INTO transactions 
                (transaction_id,account_id, transaction_type, amount, transaction_date, transaction_name, description, balance_after) 
                VALUES (?,?,?,?,?,?,?,?)
            ''', (enc_transaction_id, account_id, enc_transaction_type, enc_amount, enc_transaction_date, enc_name, enc_description, enc_new_balance))
            
            self.cursor.connection.commit()
            print(f"Successfully added transaction for account {account_id}")
            return True
            
        except Exception as e:
            print(f"Error adding transaction: {str(e)}")
            return False
    
    def get_transactions(self, account_id, limit=5, offset=0):
        try:
            print(f"Getting transactions for account_id: {account_id}")
            # Don't encrypt account_id again since it's already encrypted
            query = '''
                SELECT transaction_id, transaction_type, amount, transaction_date, transaction_name, description 
                FROM transactions 
                WHERE account_id = ? 
                ORDER BY transaction_date DESC, transaction_id DESC
                LIMIT ? OFFSET ?
            '''
            print(f"Executing query with account_id: {account_id}, limit: {limit}, offset: {offset}")
            
            self.cursor.execute(query, (account_id, limit, offset))
            result = self.cursor.fetchall()
            
            if not result:
                print("No transactions found")
                return []
                
            print(f"Found {len(result)} transactions")
            
            # Process each row properly
            decrypted_result = []
            for row in result:
                decrypted_row = []
                print(f"Processing row: {row}")
                for value in row:
                    if value is not None:
                        try:
                            decrypted_value = self.encrypt.decrypt_text(value)
                            decrypted_row.append(decrypted_value)
                            print(f"Decrypted value: {decrypted_value}")
                        except Exception as e:
                            print(f"Error decrypting value {value}: {str(e)}")
                            decrypted_row.append(str(value))
                    else:
                        decrypted_row.append(None)
                decrypted_result.append(decrypted_row)
            
            print("Final decrypted transactions:", decrypted_result)
            return decrypted_result
            
        except Exception as e:
            print(f"Error getting transactions: {str(e)}")
            return []
    
    def get_account_transactions_by_category(self, account_id, category, mode, limit=5, offset=0):
        try:
            print(f"Getting transactions for category {category}, account_id: {account_id}, mode: {mode}")
            
            # Get transactions for this account
            self.cursor.execute('''
                SELECT transaction_id, transaction_type, amount, transaction_date, description, transaction_name
                FROM transactions 
                WHERE account_id = ?
                ORDER BY transaction_date DESC
            ''', (account_id,))
            
            result = self.cursor.fetchall()
            if not result:
                return []
                
            # Filter and decrypt transactions
            decrypted_result = []
            for row in result:
                try:
                    decrypted_type = self.encrypt.decrypt_text(row[1])
                    decrypted_category = self.encrypt.decrypt_text(row[5])
                    
                    # Only include transactions matching category and mode
                    if decrypted_category == category:
                        # Mode 1: Only Withdrawals and Transfers
                        # Mode 2: Only Deposits
                        # Any other mode: All transactions
                        if (mode == 1 and decrypted_type in ['Withdrawal', 'Transfer']) or \
                        (mode == 2 and decrypted_type == 'Deposit') or \
                        (mode not in [1, 2]):
                            
                            decrypted_row = []
                            for value in row[:-1]:  # Exclude transaction_name from result
                                if value is not None:
                                    try:
                                        decrypted_value = self.encrypt.decrypt_text(value)
                                        decrypted_row.append(decrypted_value)
                                    except Exception as e:
                                        print(f"Error decrypting value: {str(e)}")
                                        decrypted_row.append(str(value))
                                else:
                                    decrypted_row.append(None)
                            decrypted_result.append(decrypted_row)
                            print(f"Added {decrypted_type} transaction for category {decrypted_category}")
                except Exception as e:
                    print(f"Error processing transaction: {str(e)}")
                    continue
                    
            print(f"Returning {len(decrypted_result)} filtered transactions")
            return decrypted_result
            
        except Exception as e:
            print(f"Error getting transactions by category: {str(e)}")
            return []

    def get_transaction_count(self, account_id):
        try:
            # account_id is already encrypted
            self.cursor.execute('SELECT COUNT(*) FROM transactions WHERE account_id = ?', (account_id,))
            count = self.cursor.fetchone()[0]
            print(f"Found {count} transactions for account")
            return count
        except Exception as e:
            print(f"Error getting transaction count: {str(e)}")
            return 0
    
    def get_category_percentages(self, account_id, mode=0):
        try:
            print(f"Getting category percentages for account_id: {account_id}, mode: {mode}")
            
            # Get all transactions first
            self.cursor.execute('''
                SELECT transaction_name, transaction_type 
                FROM transactions 
                WHERE account_id = ?
            ''', (account_id,))
            
            transactions = self.cursor.fetchall()
            if not transactions:
                return []
                
            # Decrypt and process transactions
            categories = {}
            total_count = 0
            
            for trans in transactions:
                category = self.encrypt.decrypt_text(trans[0])  # Decrypt category
                trans_type = self.encrypt.decrypt_text(trans[1])  # Decrypt transaction type
                
                # Filter based on mode
                if mode == 1 and trans_type not in ['Withdrawal', 'Transfer']:
                    continue
                elif mode == 2 and trans_type != 'Deposit':
                    continue
                elif mode not in [1, 2]:
                    # Include all transactions for other modes
                    pass
                    
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
                total_count += 1
            
            if total_count == 0:
                print(f"No transactions found for mode {mode}")
                return []
            
            # Calculate percentages
            result = []
            for category, count in categories.items():
                percentage = round((count * 100.0 / total_count), 2)
                result.append((category, count, percentage))
            
            # Sort by count in descending order
            result.sort(key=lambda x: x[1], reverse=True)
            
            print(f"Processed {len(result)} categories for mode {mode}")
            for cat in result:
                print(f"Category: {cat[0]}, Count: {cat[1]}, Percentage: {cat[2]}%")
                
            return result
            
        except Exception as e:
            print(f"Error getting category percentages: {str(e)}")
            return []
    
    def get_category_amounts(self, account_id):
        try:
            # account_id is already encrypted from get_acc_id_with_attr
            print(f"Getting category percentages for account_id: {account_id}")
            
            self.cursor.execute('''
                SELECT transaction_name, amount,
                FROM transactions
                WHERE account_id = ?
                GROUP BY transaction_name
                ORDER BY count DESC
            ''', (account_id, account_id))
            
            result = self.cursor.fetchall()
            print(f"Found {len(result)} categories")
            
            decrypted_result = []
            for value in result:
                try:
                    decrypted_category = self.encrypt.decrypt_text(value[0])
                    decrypted_result.append((decrypted_category, value[1], value[2]))
                    print(f"Processed category: {decrypted_category}")
                except Exception as e:
                    print(f"Error processing category: {str(e)}")
            
            return decrypted_result
            
        except Exception as e:
            print(f"Error getting category percentages: {str(e)}")
            return []

        

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
    try:
        email = eel.get_cookie('email')()
        print(f"Looking up transactions for email: {email}")
        
        if not email:
            print("No email found in cookie")
            return []
            
        account_id = ar.get_acc_id_with_attr('email', email)
        if account_id is None:
            print("No account ID found for email:", email)
            return []
            
        transactions = tr.get_transactions(account_id, limit, offset)
        print("Retrieved transactions (raw):", transactions)
        
        # Validate transaction data
        if transactions:
            for idx, trans in enumerate(transactions):
                print(f"Transaction {idx}:", trans)
                if len(trans) != 6:  # We expect 6 columns
                    print(f"Warning: Transaction {idx} has wrong number of columns: {len(trans)}")
                    
        return transactions
        
    except Exception as e:
        print(f"Error getting transactions: {str(e)}")
        return []

@eel.expose
def get_account_transactions_by_category(category, mode, limit=5, offset=0):
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_account_transactions_by_category(account_id, category, mode, limit, offset)

@eel.expose
def get_latest_balance():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_latest_balance(account_id)

@eel.expose
def get_transaction_count():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_transaction_count(account_id)

@eel.expose
def get_category_percentages(mode):

    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return tr.get_category_percentages(account_id, mode)