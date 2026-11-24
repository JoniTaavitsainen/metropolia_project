import random
import time

from text import clear, draw_text, input_left, print_left, print_center, print_right
from icons import get_icon
from inventory import ITEM_PRESETS, Note

# Käytä tätä tapahtuman sisällä, kun pelaajan pitää valita vaihtoehto.
def choose_option(prompt, options):
    """Näyttää pakolliset numerovalinnat ja palauttaa valitun indeksin."""
    if not options:
        raise ValueError("Valittavia vaihtoehtoja ei ole.")

    while True:
        clear()
        print_left(prompt)
        for number, option in enumerate(options, start=1):
            print_left(f"{number}. {option}")

        print_right(get_icon("exclamation"))
        
        draw_text()

        try:
            choice = int(input_left("Valitse numero: "))
        except ValueError:
            clear()
            print_left("Virheellinen valinta. Kirjoita vaihtoehdon numero.")
            draw_text()
            input_left("Paina Enter ja yritä uudelleen.")
            continue

        if 1 <= choice <= len(options):
            return choice

        clear()
        print_left("Virheellinen valinta. Valitse jokin näytetyistä numeroista.")
        draw_text()
        input_left("Paina Enter ja yritä uudelleen.")


# Käytä tätä satunnaiseen tulokseen. Anna parit muodossa (prosenttiosuus, tulos);
# prosenttiosuuksien summan pitää olla 100. Funktio palauttaa valitun tuloksen.
def choose_outcome(outcomes):
    """Palauttaa satunnaisesti valitun tuloksen prosenttiosuuksien mukaan."""
    if not outcomes or any(chance < 0 for chance, _ in outcomes):
        raise ValueError("Tuloksia pitää olla, eikä prosenttiosuus voi olla negatiivinen.")
    if sum(chance for chance, _ in outcomes) != 100:
        raise ValueError("Tulosten prosenttiosuuksien summan pitää olla 100.")

    roll = random.random() * 100
    total = 0
    for chance, outcome in outcomes:
        total += chance
        if roll <= total:
            return outcome

# Lisää uusi tapahtuma omana parametrittomana funktionaan.
def storage_building():
    """varastohuone"""

    choice = choose_option(
        "pääset lentoasemalle ja huomaat, että siinä on vanha varastorakennuksen.",
        ["Tutki varastorakennus", "Jatka matkaa"],
    )

    fuel_change = 0
    icao_code = None
    item = None
    if choice == 1:
        fuel_change = choose_outcome([(33, 1), (34, 0), (33, -1)])

        if fuel_change ==1:
            message = "tutkit varastorakennuksen ja löysit bensaa"
        elif fuel_change == -1:
            message = "varastorakennuksessa oli hämähäkkiä ja pudotit vahingossa bensakanisterin"
        else:
            message = "Tutkit laatikon, mutta se oli tyhjä"

    elif choice == 2:
        message = "Jatkat matkaa tutkimatta varastohuonea."

    return {
        "message": message,
        "fuel_change": fuel_change,
        "icao_code": icao_code,
        "item": item,
    }

def cafe():
    """kahvila"""

    choice = choose_option(
        "pääset lentoasemalle ja huomaat, että siinä on kahvila",
        ["Tutki kahvilan", "Jatka matkaa"],
    )

    fuel_change = 0
    icao_code = None
    item = None
    if choice == 1:
        fuel_change = choose_outcome([(30, 3), (70, -1)])

        if fuel_change == 3:
            icao_code = "EFVA"
            item = "kahvicupin"

            message = f"päätitt mennä kahvilaan ja takaalta löysi 3 bensakanisteria. Sait myös {item} ja lipun uuteen lentoasemaan (EFVA - Vaasa Airport)"

        else:
            message = "päätät mennä kahvilaan. pudotit ja hävitit bensakanisterin\n"
            
            
            

    elif choice == 2:
        message = "päätät jatkaa matkaa"

    return {
            "message": message,
            "fuel_change": fuel_change,
            "icao_code": icao_code,
            "item": item,
        }


def lostfound():
    """löytötavarat"""

    choice = choose_option(
        "Pääset lentoasemalle ja olet löytötarva paikassa.",
        ["Tutki löytötavarat", "Jatka matkaa"],
    )

    fuel_change = 0
    icao_code = None
    item = None

    if choice == 1:
        outcome = choose_outcome([(25, "ticket"), (50, 0), (25, "bensaa")])

        if outcome == "ticket":
            icao_code = "EFHK"
            item = "vanhan kartan"
            message = f"Löydät {item} ja lipun lentoasemalle (EFHK - Helsinki Vantaa Airport)."
        elif outcome == "bensaa":
            fuel_change = 1
            message = "Löysit ylimääräistä bensaa"
        else:
            message = "Löytötavaroista ei löytänyt mitään."

    else:
        message = "Jatkat matkaa tutkimatta löytötavaroita."

    return {
        "message": message,
        "fuel_change": fuel_change,
        "icao_code": icao_code,
        "item": item,
    }
            

    """
# palauta sanakirja, jotta pelin muu koodi voi käsitellä tapahtuman viestin ja vaikutukset.
def example():
    "Esimerkkitapahtuma, jonka voi suorittaa kutsulla run_event("example")."
    choice = choose_option(
        "Löydät pöydältä avunpyyntölapun ja suljetun laatikon.",
        ["Tutki laatikko", "Jatka matkaa"],
    )

    fuel_change = 0
    if choice == 1:
        fuel_change = choose_outcome([(33, 1), (34, 0), (33, -1)])
        if fuel_change == 1:
            message = "Tutkit laatikon ja löydät yhden bensakanisterin."
        elif fuel_change == -1:
            message = "Tutkit laatikon, säikädit hämähäkkiä ja pudotit bensakanisterin."
        else:
            message = "Tutkit laatikon, mutta se on tyhjä."
    elif choice == 2:
        message = "Jatkat matkaa tutkimatta laatikkoa."

    icao_code = "EFTP"
    item = (
        "Löysit pöydältä lapun: 'Apua tarvitaan lentoasemalla "
        f"Tampere-Pirkkala ({icao_code}).'"
    )
    

    # Säilytä nämä avaimet samoina, jotta main voi lukea tapahtuman tuloksen.
    return {
        "message": f"{item}\n{message}",
        "fuel_change": fuel_change,
        "icao_code": icao_code,
        "item": item,
    }
"""
# Kaikissa näissä olisi vaan 1. jatka, koska ne ei tee mitään muuta ku lisää variety
FILLER_DESCRIPTIONS = [
    "Kuljit {place} paikan läpi, mutta et löydä mitään hyödyllistä.",
    "Tutkit paikkaa {place} huolellisesti... Pelkkää roskaa ja pölyä.",
    "Huomasit liikkuvan asian paikalla {place}, mutta se ehti juosta pois...",
    "Paikalla {place} löydät vanhoja jalanjälkiä. Ne ei johda minnekkään.",
]
def filler_event(_, name):
    choose_option(random.choice(FILLER_DESCRIPTIONS).format(place=name), ["Jatka"])

ITEM_DESCRIPTIONS = [
    ("Paikassa {place} on kaatunut hylly. Sen alla näkyy pieni esine.", ("Koita poimia se", choose_outcome, ), ("Jatka matkaa", None)),
    ("{place}:n lähellä olevassa seinässä huomaat lukitun oven.")
]

def door_event(save, name):
    possible_options = ["Kävele ohi"]
    if save.inventory.item_count(ITEM_PRESETS['fuel']) > 0:
        possible_options.append("Sytytä tuleen (Käyttää polttoainetta)")

    if save.inventory.item_count(ITEM_PRESETS['key']) > 0:
        possible_options.append("Käytä avainta")
    option = choose_option(f"{name}:n lähellä olevassa seinässä huomaat lukitun oven.", possible_options)

    # Kävely ohi
    if option == 1:
        return

    # polttoaine
    if option == 2:
        save.inventory.remove(ITEM_PRESETS['fuel'])
        outcome = choose_outcome([(15, "huge_win"), (25, "win"), (60, "loss")])

    # avain
    if option == 3:
        save.inventory.remove(ITEM_PRESETS['key'])
        outcome = choose_outcome([(15, "max_win"), (35, "huge_win"), (35, "win"), (15, "loss")])

    match (outcome):
        case "max_win":
            print_left(f"Oven takana löytyi vastaus lappu!?!? Lue se heti tavaraluettelosta!")
            save.inventory.add(Note("Vastaus Lappu", f"Hahaha! Kukaan ei tiedä, että kaikki ihmiset meni piiloon lentoasemalle '{save.target_icao}'", "note", None))
        case "huge_win":
            amount = 3
            print_left(f"Oven takana löytyi hylätty varasto, jossa on monta polttoaine kanisteriä!\nKannat {amount} kanisteria mukana")
            save.inventory.add(ITEM_PRESETS['fuel'], amount)
        case "win":
            amount = 1
            print_left(f"Ovi johtaa varastoon, josta löytyi yksi jätetty polttoaine kanisteri.")
            save.inventory.add(ITEM_PRESETS['fuel'], amount)
        case "loss":
            print_left(f"Oven takana oli lappu... jossa lukee että käytit ajan hukkaan!")

    draw_text()

    time.sleep(3)

ITEM_GAIN_DESCRIPTIONS = [
    "Kuljit {place} paikan läpi, löydät {num}{item}!",
    "Huomaat liikkuvan koiran paikalla {place}, jahtamisen jälkee revit sen hampaista {num}{item}!",
    "Tutkit paikkaa {place}... Lattia romahtaa sinun alta! Huomaat että lattian alla oli {num}{item}."
]
ITEM_DROPS = [
    ITEM_PRESETS['fuel'], ITEM_PRESETS['key'], ITEM_PRESETS['trash']
]
def forced_item_gain_event(save, name):
    item = random.choice(ITEM_DROPS)
    amount = choose_outcome([(55, 1), (25, 2), (15, 3), (5, 4)])
    
    num = f"x{amount} " if amount > 1 else ""
    choose_option(random.choice(ITEM_GAIN_DESCRIPTIONS).format(place=name, item=item.name, num=num), ["Jatka"])
    save.inventory.add(item, amount)


FUEL_LOSS_DESCRIPTIONS = [
    "Iso koira jolla on raivotauti alkaa juosta sua päin!!! Heität kanisterii täynnä polttoainetta sitä päin.\nMenetit polttoaineen.",
    "Paikalla {place} alkaa olee tosi kylmä... Käytät polttoaineen nuotion tekemiseen.",
    "Tutkit alueen {place}... Mutta sulle tulee niin tylsä olo, että päätät heittää polttoaineen pois!???"
]
def forced_fuel_loss_event(save, name):
    choose_option(random.choice(FUEL_LOSS_DESCRIPTIONS).format(place=name), ["Jatka"])
    save.inventory.remove(ITEM_PRESETS['fuel'])

def get_fuel(save, text):
    print_left(text)
    save.inventory.add(ITEM_PRESETS['fuel'])
    time.sleep(2)


EVENT_TYPES = [filler_event, 
               forced_item_gain_event, 
               forced_fuel_loss_event,
               door_event]

def run_random_event(save, name):
    event = choose_outcome([(50, filler_event), 
                           (30, forced_item_gain_event), 
                           (10, door_event), 
                           (10, forced_fuel_loss_event)])
    return event(save, name)