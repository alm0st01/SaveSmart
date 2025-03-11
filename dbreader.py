import sqlite3
import eel
from random import randint
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime
import io

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

            # Keep trying until we get a unique transaction_id
            while True:
                transaction_id = str(randint(10**8, (10**9)-1))
                enc_transaction_id = self.encrypt.encrypt_text(transaction_id)
                
                # Check if transaction_id already exists
                transact_id_query = self.cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (enc_transaction_id,))
                if not transact_id_query.fetchone():
                    break

            # Encrypt all values for storage
            enc_transaction_type = self.encrypt.encrypt_text(transaction_type)
            enc_amount = self.encrypt.encrypt_text(str(amount))
            enc_transaction_date = self.encrypt.encrypt_text(transaction_date)
            enc_name = self.encrypt.encrypt_text(name)
            enc_description = self.encrypt.encrypt_text(description)
            enc_new_balance = self.encrypt.encrypt_text(str(new_balance))
            
            self.cursor.execute('''
                INSERT INTO transactions 
                (transaction_id, account_id, transaction_type, amount, transaction_date, transaction_name, description, balance_after) 
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
                ORDER BY transaction_date ASC, transaction_id ASC
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

    def get_monthly_averages(self, account_id):
        try:
            result = self.cursor.execute('''
                SELECT transaction_date, amount, transaction_type
                FROM transactions 
                WHERE account_id = ?
                ORDER BY transaction_date
            ''', (account_id,))
            
            transactions = result.fetchall()
            if not transactions:
                return {'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}

            # Group transactions by month and calculate sums
            monthly_totals = {}
            for trans_date, amount, trans_type in transactions:
                try:
                    date = self.encrypt.decrypt_text(trans_date)
                    amount = float(self.encrypt.decrypt_text(amount))
                    trans_type = self.encrypt.decrypt_text(trans_type)
                    month = date[:7]  # Get YYYY-MM format
                    
                    if month not in monthly_totals:
                        monthly_totals[month] = {'gains': 0, 'losses': 0}
                    
                    # Deposits are gains, Withdrawals and Transfers are losses
                    if trans_type == "Deposit":
                        monthly_totals[month]['gains'] += amount
                    else:  # Withdrawal or Transfer
                        monthly_totals[month]['losses'] -= amount  # Make losses negative
                except Exception as e:
                    print(f"Error processing transaction: {str(e)}")
                    continue

            # Calculate averages
            if monthly_totals:
                num_months = len(monthly_totals)
                total_gains = sum(month['gains'] for month in monthly_totals.values())
                total_losses = sum(month['losses'] for month in monthly_totals.values())
                
                return {
                    'avg_gains': total_gains / num_months,
                    'avg_losses': total_losses / num_months,  # Will be negative
                    'avg_net': (total_gains + total_losses) / num_months
                }
            
            return {'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}
        except Exception as e:
            print(f"Error getting monthly averages: {str(e)}")
            return {'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}

    def get_transaction(self, transaction_id):
        try:
            # Get the email from cookie
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return None

            # Get all transactions for this account to find the encrypted transaction_id
            self.cursor.execute('''
                SELECT transaction_id, transaction_type, amount, transaction_date, transaction_name, description
                FROM transactions 
                WHERE account_id = ?
            ''', (account_id,))
            
            transactions = self.cursor.fetchall()
            
            # Find the matching transaction by decrypting each ID
            for trans in transactions:
                try:
                    decrypted_id = self.encrypt.decrypt_text(trans[0])
                    if decrypted_id == transaction_id:
                        # Decrypt all transaction fields
                        return [
                            decrypted_id,
                            self.encrypt.decrypt_text(trans[1]),  # type
                            self.encrypt.decrypt_text(trans[2]),  # amount
                            self.encrypt.decrypt_text(trans[3]),  # date
                            self.encrypt.decrypt_text(trans[4]),  # name
                            self.encrypt.decrypt_text(trans[5])   # description
                        ]
                except Exception as e:
                    print(f"Error decrypting transaction: {str(e)}")
                    continue
            
            print(f"No transaction found with ID {transaction_id}")
            return None
            
        except Exception as e:
            print(f"Error getting transaction: {str(e)}")
            return None

    def delete_transaction(self, transaction_id):
        try:
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False

            # Get all transactions for this account
            self.cursor.execute('''
                SELECT transaction_id, account_id 
                FROM transactions 
                WHERE account_id = ?
            ''', (account_id,))
            
            transactions = self.cursor.fetchall()
            target_transaction_id = None
            
            # Find the matching transaction by decrypting each ID
            for trans in transactions:
                encrypted_id = trans[0]
                try:
                    decrypted_id = self.encrypt.decrypt_text(encrypted_id)
                    if decrypted_id == transaction_id:
                        target_transaction_id = encrypted_id
                        break
                except Exception as e:
                    print(f"Error decrypting transaction ID: {str(e)}")
                    continue
            
            if target_transaction_id is None:
                print(f"No transaction found with ID {transaction_id}")
                return False
                
            # Delete the transaction using the encrypted ID
            self.cursor.execute('''
                DELETE FROM transactions 
                WHERE transaction_id = ? AND account_id = ?
            ''', (target_transaction_id, account_id))
            
            self.cursor.connection.commit()
            deleted = self.cursor.rowcount > 0
            
            if deleted:
                print(f"Successfully deleted transaction {transaction_id}")
            else:
                print(f"Failed to delete transaction {transaction_id}")
                
            return deleted
            
        except Exception as e:
            print(f"Error deleting transaction: {str(e)}")
            return False

    def edit_transaction(self, transaction_id, transaction_type, amount, transaction_date, name, description):
        try:
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False

            # Get all transactions for this account to find the encrypted transaction_id
            self.cursor.execute('''
                SELECT transaction_id, account_id 
                FROM transactions 
                WHERE account_id = ?
            ''', (account_id,))
            
            transactions = self.cursor.fetchall()
            target_transaction_id = None
            
            # Find the matching transaction by decrypting each ID
            for trans in transactions:
                encrypted_id = trans[0]
                try:
                    decrypted_id = self.encrypt.decrypt_text(encrypted_id)
                    if decrypted_id == transaction_id:
                        target_transaction_id = encrypted_id
                        break
                except Exception as e:
                    print(f"Error decrypting transaction ID: {str(e)}")
                    continue
            
            if target_transaction_id is None:
                print(f"No transaction found with ID {transaction_id}")
                return False

            # Encrypt the new values
            enc_type = self.encrypt.encrypt_text(transaction_type)
            enc_amount = self.encrypt.encrypt_text(str(amount))
            enc_date = self.encrypt.encrypt_text(transaction_date)
            enc_name = self.encrypt.encrypt_text(name)
            enc_description = self.encrypt.encrypt_text(description)

            # Update the transaction
            self.cursor.execute('''
                UPDATE transactions 
                SET transaction_type = ?, amount = ?, transaction_date = ?, 
                    transaction_name = ?, description = ?
                WHERE transaction_id = ? AND account_id = ?
            ''', (enc_type, enc_amount, enc_date, enc_name, enc_description, 
                  target_transaction_id, account_id))
            
            self.cursor.connection.commit()
            updated = self.cursor.rowcount > 0
            
            if updated:
                print(f"Successfully edited transaction {transaction_id}")
            else:
                print(f"Failed to edit transaction {transaction_id}")
                
            return updated
            
        except Exception as e:
            print(f"Error editing transaction: {str(e)}")
            return False

class goals_reader:
    def __init__(self):
        connection = sqlite3.connect('sqlite/fbla-db.db')
        self.cursor = connection.cursor()
        self.ar = account_reader()
        self.tr = transaction_reader()
        self.encrypt = enc

    def add_goal(self, goal_name, target_amount, emergency_funds, due_date):
        try:
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False

            # Keep trying until we get a unique goal_id
            while True:
                goal_id = str(randint(10**8, (10**9)-1))
                enc_goal_id = self.encrypt.encrypt_text(goal_id)
                
                # Check if goal_id already exists
                goal_id_query = self.cursor.execute("SELECT * FROM goals WHERE goal_id = ?", (enc_goal_id,))
                if not goal_id_query.fetchone():
                    break

            # Encrypt all values for storage
            enc_goal_name = self.encrypt.encrypt_text(goal_name)
            enc_target_amount = self.encrypt.encrypt_text(str(target_amount))
            enc_emergency_funds = self.encrypt.encrypt_text(str(emergency_funds))
            enc_due_date = self.encrypt.encrypt_text(due_date)

            print("Adding goal with values:", {
                "name": goal_name,
                "target_amount": target_amount,
                "emergency_funds": emergency_funds,
                "due_date": due_date
            })
            
            self.cursor.execute('''
                INSERT INTO goals 
                (goal_id, account_id, goal_name, target_amount, emergency_funds, due_date) 
                VALUES (?,?,?,?,?,?)
            ''', (enc_goal_id, account_id, enc_goal_name, enc_target_amount, enc_emergency_funds, enc_due_date))
            
            self.cursor.connection.commit()
            print(f"Successfully added goal for account {account_id}")
            return True
            
        except Exception as e:
            print(f"Error adding goal: {str(e)}")
            return False

    def get_goals(self, account_id):
        try:
            print(f"Getting goals for account_id: {account_id}")
            
            self.cursor.execute('''
                SELECT goal_id, goal_name, target_amount, emergency_funds, due_date
                FROM goals 
                WHERE account_id = ?
                ORDER BY rowid DESC
            ''', (account_id,))
            
            result = self.cursor.fetchall()
            if not result:
                print("No goals found")
                return []
                
            decrypted_result = []
            for row in result:
                try:
                    decrypted_row = []
                    for value in row:
                        if value is not None:
                            decrypted_value = self.encrypt.decrypt_text(value)
                            decrypted_row.append(decrypted_value)
                        else:
                            decrypted_row.append(None)
                    decrypted_result.append(decrypted_row)
                except Exception as e:
                    print(f"Error decrypting goal: {str(e)}")
                    continue
            
            print(f"Retrieved {len(decrypted_result)} goals")
            return decrypted_result
            
        except Exception as e:
            print(f"Error getting goals: {str(e)}")
            return []

    def delete_goal(self, goal_id):
        try:
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False

            # Get all goals for this account
            self.cursor.execute('''
                SELECT goal_id, account_id 
                FROM goals 
                WHERE account_id = ?
            ''', (account_id,))
            
            goals = self.cursor.fetchall()
            target_goal_id = None
            
            # Find the matching goal by decrypting each ID
            for goal in goals:
                encrypted_id = goal[0]
                try:
                    decrypted_id = self.encrypt.decrypt_text(encrypted_id)
                    if decrypted_id == goal_id:
                        target_goal_id = encrypted_id
                        break
                except Exception as e:
                    print(f"Error decrypting goal ID: {str(e)}")
                    continue
            
            if target_goal_id is None:
                print(f"No goal found with ID {goal_id}")
                return False
                
            # Delete the goal using the encrypted ID
            self.cursor.execute('''
                DELETE FROM goals 
                WHERE goal_id = ? AND account_id = ?
            ''', (target_goal_id, account_id))
            
            self.cursor.connection.commit()
            deleted = self.cursor.rowcount > 0
            
            if deleted:
                print(f"Successfully deleted goal {goal_id}")
            else:
                print(f"Failed to delete goal {goal_id}")
                
            return deleted
            
        except Exception as e:
            print(f"Error deleting goal: {str(e)}")
            return False

    def rename_goal(self, goal_id, new_name):
        try:
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False

            # Get all goals for this account
            self.cursor.execute('''
                SELECT goal_id, account_id 
                FROM goals 
                WHERE account_id = ?
            ''', (account_id,))
            
            goals = self.cursor.fetchall()
            target_goal_id = None
            
            # Find the matching goal by decrypting each ID
            for goal in goals:
                encrypted_id = goal[0]
                try:
                    decrypted_id = self.encrypt.decrypt_text(encrypted_id)
                    if decrypted_id == goal_id:
                        target_goal_id = encrypted_id
                        break
                except Exception as e:
                    print(f"Error decrypting goal ID: {str(e)}")
                    continue
            
            if target_goal_id is None:
                print(f"No goal found with ID {goal_id}")
                return False

            # Encrypt the new name
            enc_new_name = self.encrypt.encrypt_text(new_name)
                
            # Update the goal name using the encrypted ID
            self.cursor.execute('''
                UPDATE goals 
                SET goal_name = ?
                WHERE goal_id = ? AND account_id = ?
            ''', (enc_new_name, target_goal_id, account_id))
            
            self.cursor.connection.commit()
            updated = self.cursor.rowcount > 0
            
            if updated:
                print(f"Successfully renamed goal {goal_id}")
            else:
                print(f"Failed to rename goal {goal_id}")
                
            return updated
            
        except Exception as e:
            print(f"Error renaming goal: {str(e)}")
            return False

    def edit_goal(self, goal_id, new_name, target_amount, emergency_funds, due_date):
        try:
            print(f"Received edit request with values: goal_id={goal_id}, new_name={new_name}, target_amount={target_amount}, emergency_funds={emergency_funds}, due_date={due_date}")
            
            # Get the email from cookie without encrypting it again
            email = eel.get_cookie('email')()
            account_id = self.ar.get_acc_id_with_attr('email', email)
            
            if account_id is None:
                print("Error: Could not find account ID")
                return False

            # Get all goals for this account to find the encrypted goal_id
            self.cursor.execute('''
                SELECT goal_id, account_id 
                FROM goals 
                WHERE account_id = ?
            ''', (account_id,))
            
            goals = self.cursor.fetchall()
            target_goal_id = None
            
            # Find the matching goal by decrypting each ID
            for goal in goals:
                encrypted_id = goal[0]
                try:
                    decrypted_id = self.encrypt.decrypt_text(encrypted_id)
                    print(f"Comparing goal IDs: {decrypted_id} vs {goal_id}")
                    if decrypted_id == goal_id:
                        target_goal_id = encrypted_id
                        print(f"Found matching goal ID: {target_goal_id}")
                        break
                except Exception as e:
                    print(f"Error decrypting goal ID: {str(e)}")
                    continue
            
            if target_goal_id is None:
                print(f"No goal found with ID {goal_id}")
                return False

            # Encrypt the new values
            enc_new_name = self.encrypt.encrypt_text(new_name)
            enc_target_amount = self.encrypt.encrypt_text(str(target_amount))
            enc_emergency_funds = self.encrypt.encrypt_text(str(emergency_funds))
            enc_due_date = self.encrypt.encrypt_text(due_date)

            print("Executing update query with values:", {
                "name": new_name,
                "target_amount": target_amount,
                "emergency_funds": emergency_funds,
                "due_date": due_date,
                "goal_id": target_goal_id,
                "account_id": account_id
            })

            # Update the goal using the encrypted goal_id
            self.cursor.execute('''
                UPDATE goals 
                SET goal_name = ?, target_amount = ?, emergency_funds = ?, due_date = ?
                WHERE goal_id = ? AND account_id = ?
            ''', (enc_new_name, enc_target_amount, enc_emergency_funds, enc_due_date, target_goal_id, account_id))
            
            self.cursor.connection.commit()
            updated = self.cursor.rowcount > 0
            
            print(f"Update result: {updated}")
            
            if updated:
                print(f"Successfully edited goal {goal_id}")
            else:
                print(f"Failed to edit goal {goal_id}")
                
            return updated
            
        except Exception as e:
            print(f"Error editing goal: {str(e)}")
            return False

ar = account_reader()
tr = transaction_reader()
gr = goals_reader()

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

@eel.expose
def add_goal(goal_name, target_amount, emergency_funds, due_date):
    return gr.add_goal(goal_name, target_amount, emergency_funds, due_date)

@eel.expose
def get_goals():
    account_id = ar.get_acc_id_with_attr('email', eel.get_cookie('email')())
    return gr.get_goals(account_id)

@eel.expose
def delete_goal(goal_id):
    return gr.delete_goal(goal_id)

@eel.expose
def rename_goal(goal_id, new_name):
    return gr.rename_goal(goal_id, new_name)

@eel.expose
def edit_goal(goal_id, new_name, target_amount, emergency_funds, due_date):
    return gr.edit_goal(goal_id, new_name, target_amount, emergency_funds, due_date)

@eel.expose
def get_monthly_averages():
    try:
        print("Starting get_monthly_averages...")
        email = eel.get_cookie('email')()
        print(f"Got email: {email}")
        account_id = ar.get_acc_id_with_attr('email', email)
        print(f"Got account_id: {account_id}")
        result = tr.get_monthly_averages(account_id)
        print(f"Monthly averages result: {result}")
        return result
    except Exception as e:
        print(f"Error in get_monthly_averages: {str(e)}")
        return {'avg_gains': 0, 'avg_losses': 0, 'avg_net': 0}

@eel.expose
def delete_transaction(transaction_id):
    return tr.delete_transaction(transaction_id)

@eel.expose
def edit_transaction(transaction_id, transaction_type, amount, transaction_date, name, description):
    return tr.edit_transaction(transaction_id, transaction_type, amount, transaction_date, name, description)
@eel.expose
def get_transaction(transaction_id):
    return tr.get_transaction(transaction_id)

@eel.expose
def generate_pdf_data():
    try:
        # Create an in-memory buffer for the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document with landscape orientation
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title = Paragraph("Transaction Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Get transactions from database
        transactions = get_account_transactions(100, 0)  # Get last 100 transactions
        
        if not transactions:
            # Handle no transactions case
            elements.append(Paragraph("No transactions found.", styles['Normal']))
            doc.build(elements)
            pdf_data = buffer.getvalue()
            buffer.close()
            return list(pdf_data)
        
        # Add account summary
        current_balance = sum([float(t[2]) if t[1] == 'Deposit' else -float(t[2]) for t in transactions])
        summary = Paragraph(f"Current Balance: ${current_balance:.2f}", styles['Heading2'])
        elements.append(summary)
        elements.append(Spacer(1, 12))
        
        # Get monthly averages
        monthly_data = get_monthly_averages()
        
        # Create monthly summary table
        monthly_table_data = [
            ['Monthly Summary', 'Amount'],
            ['Average Monthly Gains', f"${monthly_data['avg_gains']:.2f}"],
            ['Average Monthly Losses', f"${monthly_data['avg_losses']:.2f}"],
            ['Average Monthly Net', f"${monthly_data['avg_net']:.2f}"]
        ]
        
        # Style for the monthly summary table
        monthly_table = Table(monthly_table_data, colWidths=[2*inch, inch])
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97CADB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('SPAN', (0, 0), (1, 0)),  # Merge header cells
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(monthly_table)
        elements.append(Spacer(1, 20))
        
        # Add transactions table header
        elements.append(Paragraph("Transaction Details", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Create transactions table data with headers
        table_data = [['ID', 'Type', 'Amount', 'Date', 'Purchase Type', 'Description']]
        
        # Sort transactions by date (newest first)
        transactions.sort(key=lambda x: x[3], reverse=True)
        
        # Define column widths as percentages of page width
        available_width = landscape(letter)[0] - inch
        col_widths = [
            available_width * 0.10,  # ID
            available_width * 0.12,  # Type
            available_width * 0.12,  # Amount
            available_width * 0.15,  # Date
            available_width * 0.20,  # Purchase Type
            available_width * 0.31   # Description
        ]
        
        # Add transaction rows
        for transaction in transactions:
            try:
                # Format date
                date_str = transaction[3]
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date.strftime('%m/%d/%Y')
                except ValueError:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        formatted_date = date.strftime('%m/%d/%Y')
                    except ValueError:
                        formatted_date = date_str
                
                # Format amount
                amount = f"${float(transaction[2]):.2f}"
                
                # Create row with wrapped text
                row = [
                    Paragraph(str(transaction[0]), styles['Normal']),  # ID
                    Paragraph(str(transaction[1]), styles['Normal']),  # Type
                    Paragraph(amount, styles['Normal']),               # Amount
                    Paragraph(formatted_date, styles['Normal']),       # Date
                    Paragraph(str(transaction[4]), styles['Normal']),  # Purchase Type
                    Paragraph(str(transaction[5]), styles['Normal'])   # Description
                ]
                table_data.append(row)
            except Exception as e:
                print(f"Error processing transaction for PDF: {str(e)}")
                continue
        
        # Create the transactions table
        transactions_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        transactions_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#97CADB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Row styles
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            # Cell padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centered (data rows only)
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Type centered (data rows only)
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Amount right-aligned (data rows only)
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Date centered (data rows only)
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),    # Purchase Type left-aligned (data rows only)
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),    # Description left-aligned (data rows only)
        ]))
        
        elements.append(transactions_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return the PDF data as bytes
        return list(pdf_data)
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None
