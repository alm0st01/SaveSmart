import eel
import eel.browsers

import dbreader


main_window = eel
main_window.init('web')

@eel.expose
def new_transaction():
    transaction_eel = eel
    transaction_eel.init('web')
    transaction_eel.start('account/banking/add_transaction.html', mode='chrome', size=(400,500), position=(200,200), port=8001)
    

@eel.expose
def print_text(text):
    print(text)

main_window.start("index.html", mode='chrome', size=(1600,800))
