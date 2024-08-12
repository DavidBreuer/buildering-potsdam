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
    enc = enc.decode('utf-8') 
    return enc

# %#%########################################################################## generate map

tab = pd.read_excel("index.xlsx")

fab = dict()
fab['1'] = '1 gelb'
fab['2'] = '2 blau'
fab['3'] = '3 türkis'
fab['4'] = '4 rot'
fab['5'] = '5 lila'
fab['6'] = '6 schwarz'
fab['7'] = '6 weiß'
fab['?'] = '? pink'

tab["Grad"] = tab["Farbe"].astype(str).map(fab)

dscs = []
groups = tab.ffill().groupby('Name', sort=False)
for idg, group in groups:
    dsc = '<br><br>'.join(['<b>'+row["Beschreibung"][:2]+'</b>' + f" ({row['Grad']})" + row["Beschreibung"][2:] for idr, row in group.iterrows()])
    dscs.append(dsc)

tab.dropna(axis=0, subset=["Name"], inplace=True)
tab["Beschreibung"] = dscs

tab["Pfad"] = range(len(tab))  
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
<b>
<span style='color: Gold'>1 gelb</span> -
<span style='color: Blue'>2 blau</span> -
<span style='color: Cyan'>3 türkis</span> -
<span style='color: Red'>4 rot</span> -
<span style='color: DarkMagenta'>5 lila</span> -
<span style='color: Black'>6 schwarz</span> -
<span style='color: Gray'>7 weiß</span>
</b>
Bitte immer auf die eigene Sicherheit und andere Personen in der Nähe aufpassen.

Gutes Klettern und viel Spaß!
"""
tinouts["XintroX"] = XintroX.replace(" -\n", " - ").replace("\n", "<br>")

XcenterX = "[%s, %s]" % tuple(tab[["Lat", "Lon"]].mean())
tinouts["XcenterX"] = XcenterX

highlights = [] # ["Kanal", "Lustgarten", "Lange"]

XmarkersX = ""
for idi, (idr, row) in enumerate(tab.iterrows()):
    num = str(idi).zfill(2)
    nams = "img/%s.svg" % row["Kurzname"]
    namt = "img/%s.txt" % row["Kurzname"]
    namb = "img/aaa_berge.svg"
    if os.path.isfile(nams):
        name = nams
        img = f"<img id='small' src='{name}' width='200'/>"
    elif os.path.isfile(namt):
        name = namt
        with open(name, 'r') as file:
            link = file.read().strip()
        img = "<a href='%s' target='_blank'/>%s</a>" % (link, link)
    else:
        name = namb
        img = f"<img id='small' src='{name}' width='200'/>"
    print(idi, num, name)
    hglght = any([row["Name"].startswith(highlight) for highlight in highlights])
    # https://stackoverflow.com/questions/23567203/leaflet-changing-marker-color
    marker = f"var marker = L.marker([{row['Lat']}, {row['Lon']}]).addTo(map).bindPopup(\"<b>({num}) {row['Name']}</b><br>{img}<br>{row['Beschreibung']}\");\n" 
    if hglght:
        print("+")
        marker += "marker._icon.classList.add('huechange');"
    marker += "markers.push(marker);"
    XmarkersX += marker

tinouts["XmarkersX"] = XmarkersX

XnumberX = str(lent - 1)
tinouts["XnumberX"] = XnumberX

txt = replace_text(fin, fout, tinouts)

# %%########################################################################### obsolete: convert svg to png

inp = "img/"
out = "out/"

ink = 'inkscape --export-area-page --export-dpi 15 --export-png "%s" "%s"'

files = [file for file in os.listdir(inp) if ".svg" in file]  
for file in files[:0]:
    cmd = ink % (out+file.replace(".svg", ".png"), inp+file)
    print(cmd)
    os.system(cmd)

# %%########################################################################### obsolete: generate QR

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

base = "https://davidbreuer.github.io/buildering-potsdam/#"

XbodyX = ''
for idi, (idr, row) in enumerate(tab.iloc[:0].iterrows()):
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

# %%########################################################################### end file
