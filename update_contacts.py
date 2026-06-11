# -*- coding: utf-8 -*-
import csv, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

new_emails = {
    'Les Petits Reveurs':               'crechepetitsreveurs@gmail.com',
    'Centre Regional de la Famille':    'lacigogne@crfe.be',
    'ABChild':                          'info@abchild.com',
    'Le Jardin d\'eveil':               'jardindveil@gmail.com',
    'Les Pitchous':                     'irina.bouchat@rixensart.be',
    'La Colinette':                     'lacolinette.cpas@publilink.be',
    'La Recre':                         'larecre.cpas@lasne.be',
    'Les Petits Tambours':              'direction@lespetitstambours.be',
    'Maison d\'Enfants Montessori Kids':'info@maisondenfantsmontessori.be',
    'Petit a Petit':                    'carolinepapasbl@gmail.com',
    'Cardinal Mercier':                 'info@crechecardinalmercier.com',
    'KIRIKOU':                          'info.rixensart@fedasil.be',
    'Creche Communale de Nivelles':     'info@cpen.be',
}

new_phones = {
    'La Pyramide (CPAS)':               '010/43.28.50',
    'Petits Loups du Bauloy':           '010/41.49.07',
    'Les Poussins du Coin':             '010/41.20.34',
    'Les Colibris (CPAS)':              '010/43.93.60',
    'Pomme d\'Happy':                   '010/47.93.35',
    'Co-accueil de Limal':              '010/23.03.40',
    'Les P\'tits Mouchons':             '010/24.32.46',
    'Macanaille':                       '010/56.03.40',
    'L\'Aquarelle':                     '010/23.26.23',
    'Les P\'tits Coquins':              '02/656.08.69',
    'Bidouille':                        '02/353.07.70',
    'Les Pioux-Pious':                  '0484/97.34.40',
    'Les Arsouilles':                   '0484/97.34.40',
    'Espace 2000':                      '067/77.36.28',
    'Creche Parentale':                 '010/42.24.52',
}

def norm(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower()

rows = list(csv.DictReader(open('creches_moins_20km_limelette.csv', encoding='utf-8')))
fieldnames = list(rows[0].keys())

email_updated = phone_updated = 0

for row in rows:
    n = norm(row['Nom'])

    # Emails — only fill if empty
    if not row['Email'].strip():
        for key, val in new_emails.items():
            if norm(key) in n:
                row['Email'] = val
                print('  EMAIL  ' + row['Nom'][:50] + ' -> ' + val)
                email_updated += 1
                break

    # Phones — only fill if empty, skip "Creche Parentale" for Les Tournesols
    tel_field = row.get('Telephone', '')
    if not tel_field.strip():
        for key, val in new_phones.items():
            if norm(key) in n:
                # Don't assign generic "Creche Parentale" phone to Les Tournesols
                if key == 'Creche Parentale' and 'tournesols' in n:
                    continue
                row['Telephone'] = val
                print('  TEL    ' + row['Nom'][:50] + ' -> ' + val)
                phone_updated += 1
                break

with open('creches_moins_20km_limelette.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print('\n' + str(email_updated) + ' emails ajoutes, ' + str(phone_updated) + ' telephones ajoutes')
