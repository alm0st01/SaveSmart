import sys

import eel
import sqlite3
import bcrypt
import dbreader

print(sys.executable)

@eel.expose
def dblogin(email, password):
    return dbreader.dbreader.login(email, password)
eel.init('web')

eel.start("login.html")