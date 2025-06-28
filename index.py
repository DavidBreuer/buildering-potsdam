# %%########################################################################### prepare functions

import os
import numpy as np
import pandas as pd

def replace_text(fin, fout, tinouts):
    with open(fin, 'r') as file :
        txt = file.read()
    for tin, tout in tinouts.items():
        txt = txt.replace(tin, tout)
    with open(fout, 'w', encoding="utf-8") as file:
        file.write(txt)
    return txt
    
# downscale images
# mogrify -resize 30% *

# %#%########################################################################## generate map

tao = pd.read_csv("index.csv", sep=",")

tab = tao.copy()

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
lenp = 0
for idi, (idr, row) in enumerate(tab.iterrows()):
    num = str(idi).zfill(2)
    nams = "img/%s.svg" % row["Kurzname"]
    namt = "img/%s.txt" % row["Kurzname"]
    namb = "img/aaa_berge.svg"
    if os.path.isfile(nams):
        lenp += 1
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
    print(num, row["Kurzname"].ljust(25), name)
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

print('')
print('Spots', '\t=', len(tab))
print('Photos', '\t=', lenp)
print('Routes', '\t=', len(tao))

# %%########################################################################### end file
