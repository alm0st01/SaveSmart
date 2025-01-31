import eel

import dbreader


eel.init('web')

@eel.expose
def print_text(text):
    print(text)

eel.start("index.html", mode='chrome', size=(1600,800))
