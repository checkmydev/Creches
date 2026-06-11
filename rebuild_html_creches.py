# -*- coding: utf-8 -*-
import csv, sys, re
sys.stdout.reconfigure(encoding='utf-8')

rows = []
with open('creches_moins_20km_limelette.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def js_str(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")

lines = []
for r in rows:
    nom   = js_str(r['Nom'])
    adr   = js_str(r['Adresse'])
    cp    = r['Code Postal']
    com   = js_str(r['Commune'])
    lat   = r['Latitude']
    lon   = r['Longitude']
    email = r['Email']
    site  = r['Site_Web']
    tel   = js_str(r.get('Telephone', ''))
    lines.append(f"  {{nom:'{nom}',adresse:'{adr}',cp:'{cp}',commune:'{com}',lat:{lat},lon:{lon},email:'{email}',site:'{site}',tel:'{tel}'}}")

creches_js = 'const CRECHES = [\n' + ',\n'.join(lines) + '\n];'

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_new = re.sub(
    r'const CRECHES = \[.*?\];',
    creches_js,
    html,
    flags=re.DOTALL
)

if html_new == html:
    print("ERREUR : pattern CRECHES non trouvé dans le HTML.")
    sys.exit(1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_new)

print(f"HTML mis à jour : {len(rows)} crèches dans CRECHES[]")
