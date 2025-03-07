from cryptography.fernet import Fernet
import os

class encrypt:
    def __init__(self):
        self.key_file = 'encryption.key'
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as filekey:
                self.key = filekey.read()
        else:
            self.key = Fernet.generate_key()
            print("Key has not been previously generated. Generating...")
            with open(self.key_file, 'wb') as filekey:
                filekey.write(self.key)

        self.fernet = Fernet(self.key)
    
    def encrypt_text(self, text):
        return self.fernet.encrypt(text.encode())

    def decrypt_text(self, text):
        return self.fernet.decrypt(text).decode()


