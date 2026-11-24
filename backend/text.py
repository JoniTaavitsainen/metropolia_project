from subprocess import call
from getpass import getpass
from icons import get_icon
import shutil

# Pythonis ei oo helppoa cursor move, nii löysin tavan vaihtaa se manuaalisesti ?
# Esim C# / .NET ( https://learn.microsoft.com/en-us/dotnet/api/system.console.setcursorposition?view=net-10.0 )
# Python versio ois tää ( https://stackoverflow.com/questions/27612545/how-to-change-the-location-of-the-pointer-in-python )
## Päivitys: X ei toiminu, mutta sitä ei välttämättä edes tarvi, y oli tärkeempi
def set_cursor(y):
    print("\033[%dH" % y)

# emmä uskonu et tätä käytettäis eriksee tekstist, nii nää menee yhtee
def clear():
    clear_text()
    call('cls', shell=True)

size = shutil.get_terminal_size()

def refresh_size():
    global size
    size = shutil.get_terminal_size()

# helpompi kirjottaa jos ne on aluks eriksee idk
center_lines = []
left_lines = []
right_lines = []

# eriksee, koska tätä käytetää myös input paddaamisee
left_line_pad = 0.15

# järjestetty silleen, että se menee oikealta vasemmalle,
# jotta se "padding" ei overrideaa tekstiä.
# eka value tuplessa on se x positio multiplier, eli 0.5 ois keskellä X suunnassa
lines = [(0.85,          True, right_lines   ), 
         (0.5,           True,  center_lines ),
         (left_line_pad, False,  left_lines  )
        ]

# Tätä funktiota kutsutaan aina vikana, 
# sen jälkeen kun kaikki tarvittavat tekstit jo kutsuttiin
# (esim print_center())
def draw_text():
    # päivittää joka input, jotta se pysyy aina keskellä
    refresh_size()

    for pos, center, line in lines:
        # y pysyy samana joka line, eli suunnilleen keskellä sitä cmd ikkunaa
        y_pos = size.lines / 2 - len(lines)
        for text in line:
            x_pos = size.columns * pos
            print_position(text, center, x_pos, y_pos)
            y_pos += 1

        set_cursor(y_pos + 1)

def clear_text():
    for _, _, line in lines:
        line.clear()

def get_padding(text, center: bool, pos):
    text_len = 0
    if center:
        text_len = len(text) / 2
        if len(text) % 2 == 0:
            text_len += 1
    return " " * int(pos - text_len)

def print_padded(text, center, pos):
    text = convert_to_str(text)
    text_lines = text.splitlines()
    for line in text_lines:
        print(f"{get_padding(line, center, pos)}{line}")

def print_position(text, center, *pos):
        set_cursor(pos[1])
        print_padded(text, center, pos[0])

# koittaa pistää input jo paddattynä eli vasemmalle komennoille.
# laittaa sen myös samaa kohtaan kuin pisin teksti, en tiiä jos toi on paras tapa viel..
def input_left(text):
    text = convert_to_str(text)
    text_lines = text.splitlines()
    for l in range(len(text_lines) - 1):
        print_padded(text_lines[l], False, size.columns * left_line_pad)
    pad = max(left_lines, key=len) if len(left_lines) > 0 else ""
    return input(f"{get_padding(pad, False, size.columns * left_line_pad)}{text_lines[-1]}")

def getpass_left(text):
    pad = max(left_lines, key=len) if len(left_lines) > 0 else ""
    prompt = f"{get_padding(pad, False, size.columns * left_line_pad)}{text}"
    return getpass(prompt)


# nää kolme funktiota ois tietenki mahollist myös tehä yhtee,
# mut mun mielest tää on vaa parempi olla separate
def print_left(print):
    print_list(print, left_lines)

def print_center(print):
    print_list(print, center_lines)

def print_right(print):
    print_list(print, right_lines)

def print_list(print, list):
    print = convert_to_str(print)
    list.append(print)

def convert_to_str(text):
    try:
        return str(text)
    except:
        return f"Ei pystynyt saada viestin teksistä {text}!"

def test():
    while True:
        # Poista vanha teksti, visuaalisesti ja listoilta
        clear()

        print_center("a")
        print_center("ab")
        print_center("abc")
        print_center("Pidempi teksti test 123")

        print_left("a")
        print_left("Pidempi teksti test 123")
        print_left("ab")
        print_left("abc")

        print_right(get_icon("torn_note"))

        # tärkeää: input menee draw tekstin jälkee
        draw_text()
        input_left("Input tähän: ")

if __name__ == "__main__":
    test()