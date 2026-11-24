from text import *

class Menu():
    def __init__(self):
        self.stack = []
        self.last_menu = None

    def open(
                self,
                menu_name   = "Default",
                raw_actions = [],
                action_name = "Valitse numero: ",
                icon_name   = "default",
                optional_functions = [],
                loop_menu = False):
        
        current_menu = (menu_name, raw_actions, action_name, icon_name, optional_functions, loop_menu)
        has_previous = len(self.stack) > 0

        while True:
            actions = raw_actions # jotta se ei pysyis samana? idk
            # jos actions oli dynaaminen, eli päivettävä, niin kutsu sitä
            if callable(actions):
                actions = actions()
            elif isinstance(actions, tuple):
                if callable(actions[0]):
                    actions = actions[0](*actions[1:])

            new_menu = current_menu != self.last_menu
            previous = ("Takaisin", self.previous_menu)
            if has_previous and previous not in actions:
                    actions[0:0] = [previous]

            # Kun avaa uuden menun, poista vanhat tekstit
            clear()
            print_right(menu_name)
            print_right("")
            print_right(get_icon(icon_name))

            for i in range(len(actions)):
                print_left(f"{i}. {actions[i][0]}")
            
            # tallenna annettu funktio menu logii, jotta voi mennä takaisin
            if new_menu:
                self.stack.append(current_menu)
                self.last_menu = current_menu

            # Jos on olemassa funktioita, niin käytä ne ennen tekstin piirtämistä
            for function in optional_functions:
                if isinstance(function, tuple):
                    function[0](*function[1:])
                else:
                    function()

            draw_text()

            user_input = confirm_action(input_left(action_name), len(actions))

            # kattoo jos user_input muuttui integeriks, 
            # jos se on None tai eri (ei pitäs tapahtuu), 
            # niin se ei mee läpi ja pyytää input uudelleen
            if isinstance(user_input, int):
                # tarkistaa et action on olemassa, välillä se ei oo käytössä (None)
                action = actions[user_input]
                if not action[1]:
                    continue

                if loop_menu and len(self.stack) < 1:
                    action[1](*action[2:])
                else:
                    break

        # kutsu valittu funktio
        # ja sen argumentit (*action[2:])
        action[1](*action[2:])

    def previous_menu(self):
        if len(self.stack) < 2:
            return
        self.stack.pop() # poista tämä hetkinen menu, jotta saa sen edellisen 
        previous_menu = self.stack.pop() # edellinen menu
        self.open(*previous_menu)

    # käytetään, jos haluu mennä pari kertaa pois samalla
    # esim, poistit item inventory:sta mutta et halua että se päätyy siihen menuun uuestaa
    def remove_last_menu(self):
        self.stack.pop()

    def clear(self):
        self.stack.clear()

def confirm_action(input, action_len):
    try:
        action_num = int(input)
        if action_num < 0 or action_num >= action_len:
            return None
        
        return action_num
    except:
        return None

def example_b(numero):
    clear()
    print(f"Funktio {numero}")

def example():
    menu = Menu()
    actions = [("Avaa toinen menu", menu.open, "Toinen menu."), 
               ("Avaa funktion"   , example_b, 15            )]
    menu.open("Example 1", actions, "Valitse toiminta: ")

if __name__ == "__main__":
    example()