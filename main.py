import time
import random
import copy
from os import _exit
from sql import sql_result, sql_execute, sql_fetchone
from datetime import datetime
from icons import get_icon
from text import clear, print_left, print_center, print_right, draw_text, input_left, getpass_left
from auth import authenticate_user, create_user
from menu import Menu
from inventory import Inventory, ITEM_PRESETS, Note, Fuel, total_notes, create_notes
from events import choose_option, run_random_event

CURRENT_USER = None

def get_random_icao():
    return sql_result(f'select ident from airport where char_length(ident) = 4 order by rand({time.time()}) limit 1')[0][0] 

def get_overlined_text(text):
    new_text = "\u0336"
    for letter in text:
        new_text += letter + "\u0336"
    return new_text

def _read_credentials(confirm_password=False):
    name = input_left("Käyttäjänimi: ").strip()
    password = getpass_left("Salasana: ")
    if confirm_password:
        confirmation = getpass_left("Salasana uudelleen: ")
        if password != confirmation:
            return name, None
    return name, password

def login():
    global CURRENT_USER
    clear()
    print_left("Kirjaudu sisään")
    print_right(get_icon("auth"))
    draw_text()

    name, password = _read_credentials()
    if password is not None and authenticate_user(name, password):
        CURRENT_USER = name
        return True, "Kirjautuminen onnistui."
    else:
        CURRENT_USER = None
        return False, "Väärä käyttäjänimi tai salasana."

def new_user():
    clear()
    print_left("Luo uusi käyttäjä")
    print_right(get_icon("auth"))
    draw_text()

    name, password = _read_credentials(confirm_password=True)
    successful = False
    clear()
    if password is None:
        message = "Salasanat eivät täsmää."
    else:
        successful, message = create_user(name, password)

    return successful, message

def print_error(text):
    clear()
    print_left(text)
    print_right(get_icon("error"))
    draw_text()
    time.sleep(2)

class Save():
    def __init__(self, account_id=None, game_id=None):
        self.account_id = account_id
        self.game_id = game_id
        self.seed = self.roll_seed() # käyttää ajan, jonka perusteella rollataa asioit

        # tää olis se voittava icao koodi
        self.target_icao = self.get_wincon_sql()

        create_notes(self)

        self.menu = Menu()
        self.inventory = Inventory(self.menu)
        self.load_inventory_sql()

        # TODO
        # SQL OSA:
        # Loadaa se visited_locations dict, eikä current location, tai molemmat ?
        self.visited_locations = self.load_visited_locations_sql()
        self.update_airport(self.load_location_from_sql())

        self.last_played = self.update_last_played()

    @staticmethod
    def roll_seed():
        return str(time.time())

    def load_location_from_sql(self):
        if self.game_id is None:
            return 'EFHK'
        row = sql_fetchone(
            "SELECT location FROM game WHERE id = %s",
            (self.game_id,),
        )
        if row and row[0]:
            return row[0]
        return 'EFHK'

    def load_inventory_sql(self):
        if self.game_id is None:
            self.inventory.add(ITEM_PRESETS['fuel'], 3)
            return

        rows = sql_result(
            "SELECT item_type, item_key, item_name, item_description, icon, quantity "
            "FROM inventory WHERE game_id = %s",
            (self.game_id,),
        )
        loaded_fuel = False
        for item_type, item_key, item_name, description, icon, quantity in rows or []:
            if quantity is None or quantity < 0:
                raise ValueError(
                    f"Invalid inventory quantity for game {self.game_id}, "
                    f"item {item_key!r}."
                )
            if item_type == "fuel":
                item = ITEM_PRESETS['fuel']
                loaded_fuel = True
            elif item_type == "note":
                item = Note(item_name, description, icon, None)
            else:
                raise ValueError(
                    f"Unknown inventory item type {item_type!r} "
                    f"for game {self.game_id}."
                )
            if quantity > 0:
                self.inventory.add(item, quantity)

        if not loaded_fuel:
            fuel = ITEM_PRESETS['fuel']
            self.inventory.add(fuel, 3)
            self.save_inventory_item(fuel, 3)

    def save_inventory_item(self, item, quantity):
        if self.game_id is None:
            return

        if isinstance(item, Fuel):
            item_type = "fuel"
            item_key = "fuel"
        elif isinstance(item, Note):
            item_type = "note"
            item_key = item.name
        else:
            raise TypeError(f"Cannot save unsupported inventory item {item!r}.")

        sql_execute(
            "INSERT INTO inventory "
            "(game_id, item_type, item_key, item_name, item_description, icon, quantity) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE item_type = VALUES(item_type), "
            "item_name = VALUES(item_name), item_description = VALUES(item_description), "
            "icon = VALUES(icon), quantity = VALUES(quantity)",
            (
                self.game_id,
                item_type,
                item_key,
                item.name,
                item.description,
                item.icon,
                quantity,
            ),
        )

    def change_fuel(self, amount):
        current_amount = self.inventory.item_count(ITEM_PRESETS['fuel'])
        new_amount = max(0, current_amount + amount)

        if self.game_id is not None:
            self.save_inventory_item(ITEM_PRESETS['fuel'], new_amount)

        if amount > 0:
            self.inventory.add(ITEM_PRESETS['fuel'], new_amount - current_amount)
        elif amount < 0:
            self.inventory.remove(
                ITEM_PRESETS['fuel'],
                current_amount - new_amount,
            )

    def update_last_played(self):
        now = datetime.fromtimestamp(time.time())
        if self.account_id is not None and self.game_id is not None:
            sql_execute(
                "UPDATE game SET last_played = NOW() WHERE id = %s",
                (self.game_id,),
            )
        return now

    def update_airport(self, icao):
        icao = icao.upper()
        if icao in self.visited_locations:
            pass
        else:
            roll_events(icao, self)

        self.current_airport_icao = icao
        if self.game_id is not None:
            sql_execute(
                "UPDATE game SET location = %s WHERE id = %s",
                (icao, self.game_id),
            )
        self.update_last_played()
        self.menu.clear()

    def get_wincon_sql(self):
        row = sql_fetchone(
            "SELECT wincon FROM game WHERE id = %s",
            (self.game_id,),
        )
        if row and row[0]:
            return row[0].upper()

        target_icao = get_random_icao()
        sql_execute(
            "UPDATE game SET wincon = %s WHERE id = %s",
            (target_icao, self.game_id),
        )
        return target_icao

    def load_visited_locations_sql(self):
        if self.game_id is None:
            return {}

        rows = sql_result(
            "SELECT icao, location_name, event_type, finished "
            "FROM visited_locations WHERE game_id = %s "
            "ORDER BY icao, location_name",
            (self.game_id,),
        )
        visited_locations = {}
        for icao, location_name, event_type, finished in rows or []:
            icao = icao.upper()
            if event_type == "note":
                cmd = (note_pickup, self, location_name)
            elif event_type == "event":
                cmd = (run_random_event, self, location_name)
            else:
                raise ValueError(
                    f"Unknown event type {event_type!r} for {icao} "
                    f"location {location_name!r}."
                )

            visited_locations.setdefault(icao, []).append({
                "name": location_name,
                "cmd": cmd,
                "finished": bool(finished),
                "event_type": event_type,
            })
        return visited_locations

def get_account_id_by_name(name):
    if not name:
        return None
    row = sql_fetchone(
        "SELECT id FROM account WHERE screen_name = %s",
        (name,),
    )
    return row[0] if row else None


def get_existing_game_saves(account_id):
    if account_id is None:
        return []
    result = sql_result(
        "SELECT id, last_played FROM game WHERE account_id = %s ORDER BY last_played DESC, id DESC",
        (account_id,),
    )
    return result if result else []


def create_game_save(account_id):
    if account_id is None:
        return None
    return sql_execute(
        "INSERT INTO game (account_id, last_played) VALUES (%s, NOW())",
        (account_id,),
    )


def save_file_select(account_id):
    if account_id is None:
        return Save()

    saves = get_existing_game_saves(account_id)
    if not saves:
        new_save_id = create_game_save(account_id)
        return Save(account_id=account_id, game_id=new_save_id)

    stats = sql_fetchone(
        "SELECT win, loss FROM account WHERE id = %s",
        (account_id,),
    )
    if stats is None:
        raise ValueError(f"Account {account_id} was not found.")
    record_text = f"Wins: {stats[0]}  Losses: {stats[1]}"

    clear()
    while True:
        print_left("Valitse tallennus")
        print_right(record_text)

        print_left("1. Jatka olemassa olevaa tallennusta")
        print_left("2. Luo uusi tallennus")
        draw_text()
        choice = input_left("Valitse toiminto: ").strip()
        clear()
        if choice == "1":
            print_left("Valitse tallennus:")
            print_right(record_text)
            for index, (game_id, last_played) in enumerate(saves, start=1):
                print_left(f"{index}. {last_played}")
            draw_text()
            save_choice = input_left("Valitse numero: ").strip()
            try:
                save_index = int(save_choice) - 1
                if 0 <= save_index < len(saves):
                    game_id, _ = saves[save_index]
                    clear()
                    return Save(account_id=account_id, game_id=game_id)
            except ValueError:
                pass
            clear()
            print_center("Virheellinen valinta. Yritä uudelleen.")
            draw_text()
        elif choice == "2":
            new_save_id = create_game_save(account_id)
            return Save(account_id=account_id, game_id=new_save_id)
        else:
            print_center("Valitse 1 tai 2.")
            draw_text()

# Tätä pidetään funktiona jotta se lentoasema icao koodi päivittyy (string)
def game_actions(save: Save):
    return [
        (f"Tutki nykyisen lentoaseman ({save.current_airport_icao})", explore_airport, save),
        ("Avaa tavaraluettelo", save.inventory.open),
        ("Vaihda lentoasema", change_airport, save),
        ("Tallenna ja sulje peli", save_exit, save),
    ]

def update_exploration_actions(save):
    actions = []
    for event in save.visited_locations[save.current_airport_icao]:
        if event['finished']:
            actions.append((get_overlined_text(event['name']), None))
        else:
            actions.append((event['name'], run_event, save, event))
    return actions

def explore_airport(save: Save):
    save.menu.open("Tutkinta alueet", (update_exploration_actions, save), "Valitse alue, jonka haluat tutkia: ", "exclamation", loop_menu=True)

def run_event(save: Save, event):
    cmd = event['cmd']
    result = cmd[0](*cmd[1:])
    if isinstance(result, dict) and result.get("fuel_change", 0) != 0:
        save.change_fuel(result["fuel_change"])
    if isinstance(result, dict) and result.get("message"):
        clear()
        print_left(result["message"])
        draw_text()
        input_left("Paina Enter jatkaaksesi.")

    event['finished'] = True
    sql_execute(
        "UPDATE visited_locations SET finished = 1 "
        "WHERE game_id = %s AND icao = %s AND location_name = %s",
        (save.game_id, save.current_airport_icao, event['name']),
    )

def change_airport(save: Save):
    actions = [
        ("Vaihto ICAO-koodilla [Hinta: 3 polttoainetta]", change_airport_icao, save, 3),
        ("Vaihto satunnaiseen lentoasemaan [Hinta: 1 polttoaine]", change_airport_random, save, 1)
    ]

    save.menu.open("Lentoaseman vaihto", actions, "Valitse komento: ", "airplane")

def change_airport_icao(save: Save, price):
    amount = save.inventory.item_count(ITEM_PRESETS['fuel'])
    if amount < price:
        print_error(f"Polttoaine ei riitä! (Puuttuu {price - amount})")
        return
    
    icao = input_left("Syötä ICAO-koodi: ")
    result = sql_result(f"select name from airport where ident='{icao.upper()}'")

    current_icao = save.current_airport_icao.lower()
    if result and icao != current_icao:
        save.change_fuel(-price)
        save.update_airport(icao)
    elif icao == current_icao:
        print_error("Olet jo tällä lentoasemalla.")
    else:
        print_error("ICAO-koodi ei toiminut.")
        

def change_airport_random(save: Save, price):
    amount = save.inventory.item_count(ITEM_PRESETS['fuel'])
    if amount < price:
        print_error(f"Polttoaine ei riitä! (Puuttuu {price - amount})")
        return

    save.change_fuel(-price)
    save.update_airport(get_random_icao())


# Lappujen mahdolliset paikka alueet
# (esim vessa ei toimis lol)
NOTE_LOCATIONS = [
    "Kahvila", "Ravintola", "Info-huone", "Odotusaula",
]

RANDOM_LOCATIONS = [
    "Apteekki", "Matkatavaranouto", "Turvatarkastus"
]

NOTE_LOCATION_DESCRIPTIONS = [
    "Päätit tutkia {place}:n, josta löytyi seinässä oleva lappu.",
    "Aloitit kävelyn {place}:iä päin, mutta huomasit maassa olevaa lappua.",
    "Koitit päästää {place}:n, mutta eksyit... Matkalla kuitenkin löytyi erikoinen lappu",
    "{place}:n tutkinnan jälkeen sait yhden lapun.",
]

ALL_LOCATIONS = NOTE_LOCATIONS + RANDOM_LOCATIONS

def roll_events(icao, save: Save):
    random.seed(save.seed + icao)
    
    events = []

    possible_locations = copy.copy(ALL_LOCATIONS) # jotta ne ei looppaa, poista aina otettu
    # alussa aina lisätään yhen vihjeen, jotta se olisi 100% joka lentoasemalla
    if len(total_notes) > 0:
        note_loc = random.choice(NOTE_LOCATIONS)
        name = note_loc
        possible_locations.remove(note_loc)
        events.append({
            "name": name,
            "cmd": (note_pickup, save, name),
            "finished": False,
            "event_type": "note",
        }) 

    amount = random.randrange(2, 4)
    for _ in range(amount):
        loc = random.choice(possible_locations)
        possible_locations.remove(loc)

        events.append({
            "name": loc,
            "cmd": (run_random_event, save, loc),
            "finished": False,
            "event_type": "event",
        })

    # ja laita ne satunnaisiin kohtiin, jotta se vihje ei olisi aina ekana 
    random.shuffle(events)
    for event in events:
        sql_execute(
            "INSERT INTO visited_locations "
            "(game_id, icao, location_name, event_type, finished) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                save.game_id,
                icao,
                event["name"],
                event["event_type"],
                event["finished"],
            ),
        )
    save.visited_locations[icao] = events

def note_pickup(save: Save, name):
    # ei optionis oo välii se result on ain sama
    # mul ei oo aikaa tehä oikeest hauskoi interactionei... haluun nukkuu
    choose_option(random.choice(NOTE_LOCATION_DESCRIPTIONS).format(place=name), ["Ota mukaan"])
    print_left("Otit lapun mukaan...\nVoit lukea sitä tavaraluettelossa.")
    draw_text()

    note = total_notes.pop()
    save.inventory.add(note)
    save.save_inventory_item(note, save.inventory.item_count(note))

    time.sleep(3)

def check_win(save):
    if save.current_airport_icao == save.target_icao:
        finish_game(save, True)

    fuel_amount = save.inventory.item_count(ITEM_PRESETS['fuel'])
    airport_events = save.visited_locations.get(
        save.current_airport_icao,
        [],
    )
    has_remaining_events = any(
        not event["finished"] for event in airport_events
    )

    if fuel_amount == 0 and not has_remaining_events:
        finish_game(save, False)

def get_airport_name(icao):
    return sql_result(f"select name from airport where ident='{icao}'")[0][0]

def game(save: Save):
    while True:
        airport_name = sql_result(f"select name from airport where ident='{save.current_airport_icao}'")[0][0]
        save.menu.open(airport_name, game_actions(save), "Mitä haluat tehdä?: ", "question", [(check_win, save)])

def finish_game(save: Save, won: bool):
    if save is None or save.game_id is None or save.account_id is None:
        return

    result_column = "win" if won else "loss"
    sql_execute(
        f"UPDATE account SET `{result_column}` = `{result_column}` + 1 "
        "WHERE id = %s",
        (save.account_id,),
    )
    sql_execute(
        "DELETE FROM game WHERE id = %s AND account_id = %s",
        (save.game_id, save.account_id),
    )

    clear()
    print_left(
        "Voitit! Löysit oikealle lentoasemalle."
        if won
        else "Hävisit! Polttoaine loppui eikä lentoasemalla ole enää tutkittavaa."
    )
    print_right(get_icon("game_over"))
    draw_text()
    _exit(1)

def save_game(save: Save):
    if save is None or save.game_id is None:
        return
    sql_execute(
        "UPDATE game SET last_played = NOW() WHERE id = %s",
        (save.game_id,),
    )


def save_exit(save: Save):
    clear()
    print_left("Peli tallennettu. Kiitos pelaamisesta!")
    draw_text()

    save_game(save)
    _exit(1)

if __name__ == "__main__":
    logged_in = False
    message = ""
    icon_name = "auth"
    while True:
        clear()

        print_left("Tervetuloa peliin!")

        print_left("1. Kirjaudu sisään")
        print_left("2. Luo uusi käyttäjä")

        print_center(message)

        print_right(get_icon(icon_name))

        draw_text()

        choice = input_left("Valitse toiminto: ")
        if choice == "1":
            logged_in, message = login()
            if logged_in == False:
                icon_name = "error"
        elif choice == "2":
            success, message = new_user()
            icon_name = "checkmark" if success else "error"
        else:
            message = "Virheellinen valinta (valitse 1 tai 2). Yritä uudelleen."
            icon_name = "error"
        if logged_in == True:
            icon_name = "loading"
            break

    clear()

    print_left(message)
    print_right(get_icon(icon_name))
    draw_text()
    time.sleep(1)

    account_id = get_account_id_by_name(CURRENT_USER)
    if account_id is None:
        print_left("Kirjautumista ei voitu vahvistaa. Lopetetaan.")
        draw_text()
        time.sleep(2)
        _exit(1)

    save = save_file_select(account_id)

    print_left("Peli alkaa!")
    draw_text()

    time.sleep(2)
    game(save)