from text import print_center
from menu import Menu
from copy import copy
import random

class Item():
    def __init__(self, name, description, icon, usage):
        self.name = name
        self.description = description
        self.usage = usage
        self.icon = icon

    def get_actions(self):
        actions = []
        if not self.usage:
            actions.append(("Ei ole muuta käyttöä", None))
            return actions
        for action in self.usage:
            actions.append(action)
        return actions
    
    def show_description(self):
        print_center(f"Kuvaus:")
        print_center("")
        print_center(self.description)

class Fuel(Item):
    def __init__(self, name, description, icon, usage):
        super().__init__(name, description, icon, usage)

class Note(Item):
    def __init__(self, name, description, icon, usage):
        super().__init__(name, description, icon, usage)

class Key(Item):
    def __init__(self, name, description, icon, usage):
        super().__init__(name, description, icon, usage)

class Trash(Item):
    def __init__(self, name, description, icon, usage):
        super().__init__(name, description, icon, usage)

# Älä ees kysy miks tää on splitattu classeihi lol
ITEM_PRESETS = {
    "fuel": Fuel("Polttoaine", "Aine, jonka avulla pystyy matkustamaan lentoasemilla.\nKäytetään automaattisesti tarvittaessa.", "fuel", None),
    "key": Key("Avain", "Yleisavain... ehkä tätä on mahdollista käyttää johonkin?", "key", None),
    "trash": Trash("Roska", "Ei mitään käyttöö.. Miksi ikinä ottaisit tämän...?", "question", None)
}

NOTE_DESCRIPTIONS = ["Selviytyjät!!! Kokoonnutaan kaikki lentokentällä {fill}...", 
                     "Kaikki j#lj##lä ole... ihmiset! Tulkaa kentälle {fill}...", 
                     "Suunta... {fill}, pysykää elossa!", 
                     "Radiosta kuului koodi {fill}, menossa sinne! T: I...",
                     "KAIKKI KUOLEE!!! PELASTUSTA EI LÖYDY... PAITSI? KENTÄLLÄ {fill}"]
NOTE_ICONS = ["note", "torn_note"]

total_notes = []
def create_notes(save):
    desc = copy(NOTE_DESCRIPTIONS)

    for i in range(len(save.target_icao)):
        note_desc = random.choice(desc)
        desc.remove(note_desc)
        fill = "****"[:i] + save.target_icao[i] + "****"[i + 1:]
        total_notes.append(Note(f"Vihje lappu {i}", note_desc.format(fill=fill), random.choice(NOTE_ICONS), None))

    random.shuffle(total_notes)

class Inventory():
    def __init__(self, menu: Menu, starting_items = {}):
        self.item_list = starting_items
        self.item_list: dict
        self.menu = menu

    # erikseen, jotta sen voi kutsuu joka kerta ku avaa tavaraluettelon,
    # eikä yhden kerran lista
    def get_item_actions(self):
        item_actions = []
        for item in self.item_list.keys():
            amount = self.item_list.get(item, 0)
            item_count = f"x{amount}" if amount > 1 else ""
            item_actions.append((f"{item.name} {item_count}", self.open_item_info, item))

        return item_actions

    def open(self):
        self.menu.open("Tavaraluettelo", self.get_item_actions, "Valitse tavara: ", "inventory")

    def add(self, item: Item, count = 1):
        self.item_list[item] = self.item_list.get(item, 0) + count

    def remove(self, item: Item, count = 1):
        amount = self.item_list.get(item, 0) - count
        if amount > 0:
            self.item_list[item] = amount
        else:
            self.item_list.pop(item, None)

    def item_count(self, item: Item):
        return self.item_list.get(item, 0)

    # eri ku item_count koska Note olis eri objektit, eikä samat niiku polttoaineet.
    def type_count(self, item_type):
        total = 0
        for item, count in self.item_list.items():
            if isinstance(item, item_type):
                total += count
        return total

    def open_item_info(self, item: Item):
        self.menu.open(item.name, item.get_actions(), "Valitse tavaran käyttö: ", item.icon, [(item.show_description)])


# TBH nää esimerkit ei enää toimi kosk vaihoin monet classeiks lmao
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# def test_use(item):
#     item_list.remove(item)
#     # perjatteessa tekee sillee, että se skippaa 
#     # item menun, niin et voi käyttää samaa item joka oli jo poistettu uudestaan
#     remove_last_menu()

#     open_menu(f"{item.name} käytetty!", action_name="Sait käytettyy test tavaran!\nValitse numero: ", icon_name="checkmark")

# Esimerkki käytöstä
# if __name__ == "__main__":
#     inv = Inventory()
#     t = Item("Lappu", "Lappu, jossa saattaa lukea vihje...", "note", None)
#     t.usage = [("Käytä", test_use, t), ("Sulje peli (???)", print, "Tehty.")]

#     item_list.append(t)
#     inv.open()