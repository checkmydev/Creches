# -*- coding: utf-8 -*-
"""Ajoute les nouvelles crèches au CSV avec géocodage via Nominatim."""
import csv, json, time, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

NEW_CRECHES = [
    {'Nom': 'Les Joyeux Lurons',        'Adresse': 'Chaussée de Bruxelles 67A', 'Code Postal': '1300', 'Commune': 'Wavre',                  'Email': 'lesjoyeuxlurons@gmail.com',          'Site_Web': 'joyeuxlurons.be',           'Telephone': '010/22.41.01'},
    {'Nom': 'Les Farfadets',             'Adresse': 'Chaussée de Namur 227',     'Code Postal': '1300', 'Commune': 'Wavre',                  'Email': 'creche.farfadets@silva-medical.be',  'Site_Web': '',                          'Telephone': '010/51.95.01'},
    {'Nom': 'La Quenique',               'Adresse': 'Rue de la Quenique 1C',     'Code Postal': '1490', 'Commune': 'Court-Saint-Étienne',    'Email': 'saec@court-st-etienne.be',           'Site_Web': 'court-st-etienne.be',       'Telephone': '010/61.73.01'},
    {'Nom': 'Les Petits Paveurs',        'Adresse': "Rue de l'Église 25",        'Code Postal': '1410', 'Commune': 'Waterloo',               'Email': 'enfance@waterloo.be',                'Site_Web': 'waterloo.be',               'Telephone': '02/354.30.33'},
    {'Nom': "L'Île aux Bébés",           'Adresse': 'Avenue du Sagittaire 14',   'Code Postal': '1410', 'Commune': 'Waterloo',               'Email': 'enfance@waterloo.be',                'Site_Web': 'waterloo.be',               'Telephone': '02/357.24.24'},
    {'Nom': 'Le Lièvre et la Tortue',    'Adresse': 'Avenue des Sansonnets 12',  'Code Postal': '1410', 'Commune': 'Waterloo',               'Email': 'info@lievre-tortue.be',              'Site_Web': '',                          'Telephone': '02/883.26.70'},
    {'Nom': 'Arthur et Zoé',             'Adresse': 'Drève Richelle 161N 74',    'Code Postal': '1410', 'Commune': 'Waterloo',               'Email': 'crechearthuretzoe@gmail.com',        'Site_Web': 'arthuretzoe.be',            'Telephone': '02/351.46.52'},
    {'Nom': 'Le Petit Favia',            'Adresse': 'Champ du Favia 6',          'Code Postal': '1457', 'Commune': 'Walhain',                'Email': '',                                   'Site_Web': 'walhain.be',                'Telephone': '010/65.38.30'},
    {'Nom': "Les P'tits Loups (Walhain)",'Adresse': 'Champ du Favia 2',          'Code Postal': '1457', 'Commune': 'Walhain',                'Email': 'lesptitsloups@crfe.be',              'Site_Web': '',                          'Telephone': '010/65.90.47'},
    {'Nom': 'La Grange aux Lucioles',    'Adresse': 'Rue Colonel Vendeur 5',     'Code Postal': '1450', 'Commune': 'Chastre',                'Email': 'lagrangeauxlucioles@hotmail.com',    'Site_Web': '',                          'Telephone': '081/61.74.44'},
    {'Nom': 'La Farandole',              'Adresse': 'Avenue des Marronniers 36', 'Code Postal': '1450', 'Commune': 'Chastre',                'Email': 'asbllafarandole@hotmail.com',        'Site_Web': '',                          'Telephone': '010/65.09.47'},
    {'Nom': "Les P'tits Mousses",        'Adresse': 'Rue de Gembloux 2',         'Code Postal': '1450', 'Commune': 'Cortil-Noirmont',        'Email': '',                                   'Site_Web': '',                          'Telephone': '081/62.27.10'},
    {'Nom': 'Le Berceau (CPAS)',         'Adresse': 'Parc Prés Saint-Pierre 50', 'Code Postal': '1495', 'Commune': 'Marbais (Villers-la-Ville)', 'Email': 'petiteenfance@cpas-villerslaville.be', 'Site_Web': '',                   'Telephone': '0484/97.34.40'},
]

def geocode(adresse, cp, commune):
    q = f"{adresse}, {cp} {commune}, Belgium"
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({
        'q': q, 'format': 'json', 'limit': 1, 'countrycodes': 'be'
    })
    req = urllib.request.Request(url, headers={'User-Agent': 'creches-limelette/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f'  ⚠ Geocode error: {e}')
    return None, None

# Lire le CSV existant
with open('creches_moins_20km_limelette.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

existing_noms = {r['Nom'].strip().lower() for r in rows}

added = 0
for c in NEW_CRECHES:
    if c['Nom'].lower() in existing_noms:
        print(f'  SKIP (déjà présent) : {c["Nom"]}')
        continue
    print(f'  Géocodage : {c["Nom"]} ...', end=' ')
    lat, lon = geocode(c['Adresse'], c['Code Postal'], c['Commune'])
    if lat is None:
        # Fallback: geocode par CP + commune seulement
        lat, lon = geocode('', c['Code Postal'], c['Commune'])
    if lat is None:
        print('ÉCHEC — ignoré')
        continue
    print(f'{lat:.5f}, {lon:.5f}')
    rows.append({
        'Nom':                  c['Nom'],
        'Adresse':              c['Adresse'],
        'Code Postal':          c['Code Postal'],
        'Commune':              c['Commune'],
        'Distance_approx_km':   '',
        'Latitude':             f'{lat:.7f}',
        'Longitude':            f'{lon:.7f}',
        'Email':                c['Email'],
        'Site_Web':             c['Site_Web'],
        'Telephone':            c['Telephone'],
    })
    added += 1
    time.sleep(1)  # respecter le rate-limit Nominatim

with open('creches_moins_20km_limelette.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'\n✓ {added} crèche(s) ajoutée(s) — total : {len(rows)}')
