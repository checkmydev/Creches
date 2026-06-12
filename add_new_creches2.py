# -*- coding: utf-8 -*-
"""Ajoute la 2e vague de nouvelles crèches au CSV avec géocodage via Nominatim."""
import csv, json, time, sys, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

NEW_CRECHES = [
    # Braine-l'Alleud
    {'Nom': "Crèche Allard",                  'Adresse': 'Avenue Alphonse Allard 101',    'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'creche.allard@braine-lalleud.be',      'Site_Web': 'braine-lalleud.be', 'Telephone': '02/384.09.91'},
    {'Nom': "Crèche du Centre",               'Adresse': 'Avenue Léon Jourez 37',         'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'creche.centre@braine-lalleud.be',      'Site_Web': 'braine-lalleud.be', 'Telephone': '02/384.61.56'},
    {'Nom': "La Ribambelle (Braine)",         'Adresse': 'Rue des Mésanges Bleues 57',    'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'ribambelle@braine-lalleud.be',         'Site_Web': 'braine-lalleud.be', 'Telephone': '02/387.26.52'},
    {'Nom': "Les Mazindjes",                  'Adresse': 'Clos du Colbie 20',             'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'mazindjes@braine-lalleud.be',          'Site_Web': 'braine-lalleud.be', 'Telephone': '02/385.39.67'},
    {'Nom': "Les P'tits Dragons de l'Estrée",'Adresse': "Chaussée d'Alsemberg 154bis",   'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'petiteenfance@braine-lalleud.be',      'Site_Web': 'braine-lalleud.be', 'Telephone': '02/385.64.44'},
    {'Nom': "Au Bois Joli",                   'Adresse': 'Avenue du Bois Amory 9A',       'Code Postal': '1428', 'Commune': 'Lillois-Witterzée',           'Email': 'petiteenfance@braine-lalleud.be',      'Site_Web': 'braine-lalleud.be', 'Telephone': '02/384.15.23'},
    {'Nom': "Les Ouistitis (Braine)",         'Adresse': "Chaussée d'Alsemberg 161B",     'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'lesouistitis@outlook.com',             'Site_Web': 'lesouistitis.be',   'Telephone': '02/850.50.01'},
    {'Nom': "Ô comme 3 Pommes",              'Adresse': 'Avenue Albert Ier 78',           'Code Postal': '1420', 'Commune': "Braine-l'Alleud",            'Email': 'oco3pommes@gmail.com',                 'Site_Web': '',                  'Telephone': '02/385.13.03'},
    {'Nom': "Les Petits Papillons",           'Adresse': 'Rue de Dinant 13',              'Code Postal': '1421', 'Commune': 'Ophain-Bois-Seigneur-Isaac',  'Email': '',                                     'Site_Web': '',                  'Telephone': '02/852.11.33'},
    # Chaumont-Gistoux
    {'Nom': "Bruyères et Coquelicots",        'Adresse': 'Rue du Moulin 27',              'Code Postal': '1325', 'Commune': 'Chaumont-Gistoux',            'Email': 'directioncreche@chaumont-gistoux.be',  'Site_Web': 'chaumont-gistoux.be','Telephone': '010/68.96.65'},
    {'Nom': "Chant de Blés",                  'Adresse': 'Rue du Moulin 27A',             'Code Postal': '1325', 'Commune': 'Chaumont-Gistoux',            'Email': 'directioncreche@chaumont-gistoux.be',  'Site_Web': 'chaumont-gistoux.be','Telephone': '010/68.96.65'},
    {'Nom': "Bouton d'Or",                    'Adresse': 'Rue du Moulin 27B',             'Code Postal': '1325', 'Commune': 'Chaumont-Gistoux',            'Email': 'directioncreche@chaumont-gistoux.be',  'Site_Web': 'chaumont-gistoux.be','Telephone': '010/68.93.20'},
    {'Nom': "Crèche Perez",                   'Adresse': 'Rue du Village 5',              'Code Postal': '1325', 'Commune': 'Dion-Valmont',                'Email': 'alizee.dekeyzer@cpas1325.be',          'Site_Web': 'chaumont-gistoux.be','Telephone': '0490/42.09.20'},
    {'Nom': "Les P'tits Loups (Chaumont)",    'Adresse': 'Rue du Village 19',             'Code Postal': '1325', 'Commune': 'Chaumont-Gistoux',            'Email': 'martine.speileux@yahoo.fr',            'Site_Web': '',                  'Telephone': '010/68.99.84'},
    # Grez-Doiceau
    {'Nom': "Baby-Boom",                      'Adresse': 'Clos des Papeteries 2',         'Code Postal': '1390', 'Commune': 'Grez-Doiceau',                'Email': 'babyboom@grez-doiceau.be',             'Site_Web': 'grez-doiceau.be',   'Telephone': '010/81.51.16'},
    {'Nom': "Baby-Club",                      'Adresse': 'Rue des Béguinages 23',         'Code Postal': '1390', 'Commune': 'Grez-Doiceau',                'Email': 'babyclub@grez-doiceau.be',             'Site_Web': 'grez-doiceau.be',   'Telephone': '010/84.44.95'},
    {'Nom': "Baby-Cool",                      'Adresse': 'Rue Constant Wauters 12',       'Code Postal': '1390', 'Commune': 'Bossut-Gottechain',           'Email': 'babycool@grez-doiceau.be',             'Site_Web': 'grez-doiceau.be',   'Telephone': '010/45.96.58'},
    # Lasne
    {'Nom': "Les Marmousets",                 'Adresse': 'Place Communale 1',             'Code Postal': '1380', 'Commune': 'Lasne',                       'Email': 'pregardiennatlesmarmousets@hotmail.com','Site_Web': 'lasne.be',          'Telephone': '02/634.05.74'},
    {'Nom': "La Petite Grenouillère",         'Adresse': 'Rue du Smohain 6',              'Code Postal': '1380', 'Commune': 'Ohain',                       'Email': '',                                     'Site_Web': 'creche-lasne.be',   'Telephone': '02/642.99.33'},
    {'Nom': "Les P'tites Canailles",          'Adresse': 'Rue du Mont Lassy 31',          'Code Postal': '1380', 'Commune': 'Ohain',                       'Email': '',                                     'Site_Web': '',                  'Telephone': '02/353.09.78'},
    # Mont-Saint-Guibert
    {'Nom': "Les P'tits Filous",              'Adresse': 'Rue des Hirondelles 15',        'Code Postal': '1435', 'Commune': 'Corbais',                     'Email': 'lespetitsfilous@gmail.com',            'Site_Web': '',                  'Telephone': '010/65.57.61'},
    # Perwez
    {'Nom': "Les Oisillons (Perwez)",         'Adresse': 'Rue Lepage 17',                 'Code Postal': '1360', 'Commune': 'Perwez',                      'Email': 'info@lesoisillons.be',                 'Site_Web': 'lesoisillons.be',   'Telephone': '081/65.59.09'},
    {'Nom': "Les Bouts'Chou",                 'Adresse': 'Chaussée de Wavre 97',          'Code Postal': '1360', 'Commune': 'Perwez',                      'Email': 'lesboutschou@crfe.be',                 'Site_Web': 'crfe.info',         'Telephone': '081/64.00.49'},
    {'Nom': "Les Moussaillons",               'Adresse': 'Chaussée de Wavre 228',         'Code Postal': '1360', 'Commune': 'Perwez',                      'Email': 'lesmoussaillons.perwez@gmail.com',     'Site_Web': '',                  'Telephone': '081/22.06.11'},
    {'Nom': "Les Pitchouns",                  'Adresse': 'Avenue des Chasseurs Ardennais 12','Code Postal': '1360','Commune': 'Perwez',                    'Email': 'lespitchouns@crfe.be',                 'Site_Web': 'crfe.info',         'Telephone': '081/22.27.74'},
    # Incourt
    {'Nom': "Les Diablotins du Pachy",        'Adresse': 'Rue du Pachy 21A',              'Code Postal': '1315', 'Commune': 'Incourt',                     'Email': 'info@creche.incourt.be',               'Site_Web': 'incourt.be',        'Telephone': '010/84.63.68'},
    {'Nom': "Bébé Futé",                      'Adresse': 'Place 2',                       'Code Postal': '1315', 'Commune': 'Incourt',                     'Email': 'bebefute@live.be',                     'Site_Web': '',                  'Telephone': '010/88.80.14'},
    # Genappe
    {'Nom': "Les Croq'Notes",                 'Adresse': 'Rue du Sclage 15',              'Code Postal': '1470', 'Commune': 'Bousval',                     'Email': 'crechelescroqnotes@gmail.com',         'Site_Web': 'lacademiedesenfants.be','Telephone': '010/61.43.84'},
    {'Nom': "Abracadabra",                    'Adresse': 'Rue Saint-Joseph 6',            'Code Postal': '1471', 'Commune': 'Loupoigne',                   'Email': 'crecheabracadabra@gmail.com',          'Site_Web': 'lacademiedesenfants.be','Telephone': '067/77.10.38'},
    {'Nom': "Les Petits Matelots",            'Adresse': 'Rue de Namur 15C',              'Code Postal': '1476', 'Commune': 'Houtain-le-Val',              'Email': 'inscription.lespetitsmatelots@outlook.com','Site_Web': 'lespetitsmatelots.sitew.be','Telephone': '067/85.05.13'},
    # Villers-la-Ville
    {'Nom': "Les Pious-Pious",                'Adresse': 'Rue du Berceau 44',             'Code Postal': '1495', 'Commune': 'Marbais (Villers-la-Ville)',  'Email': 'petiteenfance@cpas-villerslaville.be', 'Site_Web': 'villers-la-ville.be','Telephone': '0484/97.34.40'},
    # Waterloo
    {'Nom': "Les Arsouilles (Waterloo)",      'Adresse': 'Rue Sainte-Anne 51',            'Code Postal': '1410', 'Commune': 'Waterloo',                    'Email': 'enfance@waterloo.be',                  'Site_Web': 'waterloo.be',       'Telephone': '02/354.95.06'},
    {'Nom': "Allo Caroline Ici Bébé",         'Adresse': 'Rue de la Station 22',          'Code Postal': '1410', 'Commune': 'Waterloo',                    'Email': 'creche2214@yahoo.fr',                  'Site_Web': '',                  'Telephone': '0484/71.37.84'},
    {'Nom': "Aux Petits Pieds",               'Adresse': 'Rue de la Station 168',         'Code Postal': '1410', 'Commune': 'Waterloo',                    'Email': '',                                     'Site_Web': '',                  'Telephone': '0478/44.78.32'},
    # Céroux-Mousty
    {'Nom': "a.bebe.c",                       'Adresse': 'Rue du Commerce 4',             'Code Postal': '1341', 'Commune': 'Céroux-Mousty',               'Email': 'crecheabebec@gmail.com',               'Site_Web': 'lacademiedesenfants.be','Telephone': '010/77.17.51'},
    # Nivelles
    {'Nom': "Les Trois Petits Pas",           'Adresse': 'Avenue de France 2',            'Code Postal': '1400', 'Commune': 'Nivelles',                    'Email': 'amandine.wautie@cpen.be',              'Site_Web': 'cpen.be',           'Telephone': '067/21.26.11'},
    {'Nom': "Les Ouistitis (Nivelles)",       'Adresse': 'Rue du Bosquet 22',             'Code Postal': '1400', 'Commune': 'Nivelles',                    'Email': 'laurence.sibille@cpen.be',             'Site_Web': 'cpen.be',           'Telephone': '067/21.26.11'},
    {'Nom': "Les Bengalis",                   'Adresse': 'Rue des Palvoles 9',            'Code Postal': '1400', 'Commune': 'Nivelles',                    'Email': 'info@cpen.be',                         'Site_Web': 'cpen.be',           'Telephone': '067/21.26.11'},
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
        print(f'  geocode error: {e}')
    return None, None

with open('creches_moins_20km_limelette.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

existing_noms = {r['Nom'].strip().lower() for r in rows}

added = skipped = failed = 0
for c in NEW_CRECHES:
    if c['Nom'].lower() in existing_noms:
        print(f'  SKIP : {c["Nom"]}')
        skipped += 1
        continue
    print(f'  Géocodage : {c["Nom"]} ...', end=' ', flush=True)
    lat, lon = geocode(c['Adresse'], c['Code Postal'], c['Commune'])
    if lat is None:
        lat, lon = geocode('', c['Code Postal'], c['Commune'])
    if lat is None:
        print('ECHEC')
        failed += 1
        continue
    print(f'{lat:.5f}, {lon:.5f}')
    rows.append({
        'Nom': c['Nom'], 'Adresse': c['Adresse'],
        'Code Postal': c['Code Postal'], 'Commune': c['Commune'],
        'Distance_approx_km': '',
        'Latitude': f'{lat:.7f}', 'Longitude': f'{lon:.7f}',
        'Email': c['Email'], 'Site_Web': c['Site_Web'], 'Telephone': c['Telephone'],
    })
    added += 1
    time.sleep(1)

with open('creches_moins_20km_limelette.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'\n{added} ajoutees, {skipped} ignorees (doublons), {failed} echecs — total : {len(rows)}')
