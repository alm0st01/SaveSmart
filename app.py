import eel
import eel.browsers

import dbreader


main_window = eel
main_window.init('web')
    

@eel.expose
def print_text(text):
    print(text)

main_window.start("index.html", mode='chrome', size=(1600,700))