import os

# ikonien sijainti
path = 'data'
files = os.listdir(path)

icon_dict = {}
for file in files:
    if not file.endswith('.icon'):
        continue
    
    with open(f"{path}/{file}", encoding='utf-8') as f:
        icon_dict[file.removesuffix('.icon')] = f.read()
        
def get_icon(name = "default"):
    try:
        return icon_dict[name.lower()]
    except:
        return icon_dict["default"]
