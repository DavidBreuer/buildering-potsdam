# %%########################################################################### prepare functions

import base64
import os
import numpy as np
import pandas as pd
import qrcode

def replace_text(fin, fout, tinouts):
    with open(fin, 'r') as file :
        txt = file.read()
    for tin, tout in tinouts.items():
        txt = txt.replace(tin, tout)
    with open(fout, 'w', encoding="utf-8") as file:
        file.write(txt)
    return txt

def replace_img(name):
    with open(name, "rb") as file:
        enc = base64.b64encode(file.read())
    enc = enc.decode('utf-8')    # convert bytes to string
    return enc

# %#%#

# https://neocities.org/
# https://temp-mail.org
## file:///media/Volume/Programs/NCBY/aws/buildering/index.html#02

# %#%########################################################################## generate map

tab = pd.read_excel("info.xlsx")

dscs = []
groups = tab.ffill().groupby('Name', sort=False)
for idg, group in groups:
    dsc = '<br><br>'.join(['<b>'+val[:2]+'</b>' + val[2:] for val in group["Beschreibung"]])
    dscs.append(dsc)

tab.dropna(axis=0, subset=["Name"], inplace=True)
tab["Beschreibung"] = dscs

tab["Pfad"] = range(len(tab))  # tab["Pfad"].astype(float).astype(int).astype(str).str.zfill(2)
lent = len(tab)

fin = "temp.html"
fout = "index.html"

tinouts = dict()

XintroX = """
<b>Willkommen bei Buildering Spots Potsdam</b>

Das Wort Buildering ist eine Mischung aus Building (engl. Gebäude) und Bouldering (engl. an Felsen klettern) und bezeichnet das Klettern an von Menschen geschaffenen Strukturen.

Klicke auf einen Marker in der Karte um mehr Informationen und Fotos zu möglichen Klettereien zu bekommen.

Über die Pfeiltasten oben kannst du auch direkt von einem zum nächsten Spot springen.

Schwierigkeitsskala:
<b><span style='color: Gold'>gelb</span> -
<span style='color: Blue'>blau</span> -
<span style='color: Cyan'>türkis</span> -
<span style='color: Red'>rot</span> -
<span style='color: DarkMagenta'>lila</span> -
<span style='color: Black'>schwarz</span></b>

Bitte immer auf die eigene Sicherheit und andere Personen in der Nähe aufpassen.

Gutes Klettern und viel Spaß!
"""
tinouts["XintroX"] = XintroX.replace(" -\n", " - ").replace("\n", "<br>")

XcenterX = "[%s, %s]" % tuple(tab[["Lat", "Lon"]].mean())
tinouts["XcenterX"] = XcenterX

highlights = ["Kanal", "Lustgarten", "Lange"]

XmarkersX = ""
for idi, (idr, row) in enumerate(tab.iterrows()):
    num = str(idi).zfill(2)
    name = "img/%s.png" % row["Kurzname"]
    print(name)
    if not os.path.isfile(name):
        print("-")
        name = "img/%s.txt" % row["Kurzname"]
        if not os.path.isfile(name):
            name =  "img/aaa_berge.jpg"
    if '.png' in name or '.jpg' in name:
        img = "<img id='small' src='%s' width='200'/>" % name
    else:
        with open(name, 'r') as file:
            link = file.read().strip()
        img = "<a href='%s' target='_blank'/>%s</a>" % (link, link)
    hglght = any([row["Name"].startswith(highlight) for highlight in highlights])
    # https://stackoverflow.com/questions/23567203/leaflet-changing-marker-color
    marker = "var marker = L.marker([%s, %s]).addTo(map).bindPopup(\"<b>(%s) %s</b><br>%s<br>%s\");\n" % (row['Lat'], row['Lon'], num, row['Name'], img, row["Beschreibung"])
    if hglght:
        print("+")
        marker += "marker._icon.classList.add('huechange');"
    marker += "markers.push(marker);"
    XmarkersX += marker

tinouts["XmarkersX"] = XmarkersX

colors = dict()
colors['A'] = 'blue'
colors['B'] = 'red'
colors['C'] = 'gray'
colors['D'] = 'gray'
colors['E'] = 'gray'
groups = tab.groupby('Pfad')
# letters = np.unique(list(''.join(np.hstack(tab['Pfad']))))
# groups = {letter: tab.loc[[idr for idr, row in tab.iterrows() if letter in row['Pfad']]] for letter in letters}
XpolygonX = ""

leng = len(groups)
for idi, (idg, group) in enumerate(groups):
    print(idi, leng)
    col = colors.get(idg, "black")
    XpolygonX += "var polygon = L.polyline([\n"
    for idr, row in group.iterrows():
        XpolygonX += "[%s, %s]," % (row['Lat'], row['Lon'])
    XpolygonX += "]).setStyle({color: '%s'}).addTo(map).bindPopup('Route %s');\n" % (col, col)
tinouts["XpolygonX"] = XpolygonX

XnumberX = str(lent - 1)
tinouts["XnumberX"] = XnumberX

txt = replace_text(fin, fout, tinouts)

# %%########################################################################## convert svg to png

inp = "orig/"
out = "img/"

ink = 'inkscape --export-area-page --export-dpi 15 --export-png "%s" "%s"'

files = [file for file in os.listdir(inp) if ".svg" in file]  #  and "havelbucht" in file
for file in files:
    cmd = ink % (out+file.replace(".svg", ".png"), inp+file)
    print(cmd)
    os.system(cmd)

# %#%########################################################################## generate QR

temp = """
<!DOCTYPE html>
<html>
<head>
	<title>Buildering Spots Potsdam</title>
	<meta charset="UTF-8" />
</head>
<body>
XbodyX
</body>
</html>
"""

base = "file:///media/Volume/Programs/NCBY/aws/buildering/index.html#"
base = "http://sdsd.com/index.html#"
base = "https://btp.neocities.org/#"

XbodyX = ''
for idi, (idr, row) in enumerate(tab.iterrows()):
    num = str(idi).zfill(2)
    url = base + str(idi)
    img = qrcode.make(url)
    imn = "qr/%s.png" % row['Kurzname']
    img.save(imn)
    enc = replace_img(imn)
    XbodyX += "<h3>(%s) %s</h3>\n" % (num, row['Name'])
    XbodyX += "<img src='data:image/png;base64,%s'/>" % enc

temp = temp.replace("XbodyX", XbodyX)

with open('qrcode.html', 'w', encoding="UTF-8") as file:
    file.write(temp)

# %%#
