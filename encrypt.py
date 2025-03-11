from cryptography.fernet import Fernet
import os

class encrypt: # Class used to encrypt and decrypt text with a given key
    def __init__(self):
        self.key_file = 'encryption.key'
        if os.path.exists(self.key_file): # Checks if a key already exists
            with open(self.key_file, 'rb') as filekey:
                self.key = filekey.read()
        else: 
            # If a key does not already exist, a new one will be created. 
            # This is only needed if the user has just started using the application.
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as filekey:
                filekey.write(self.key)

        self.fernet = Fernet(self.key)
    
    def encrypt_text(self, text): # Function used to encrypt text
        return self.fernet.encrypt(text.encode())

    def decrypt_text(self, text): # Function used to decrypt text
        return self.fernet.decrypt(text).decode()


