# -*- coding: utf-8 -*-
"""
Tableau de bord du suivi des crèches.

Usage :
  1. Exportez le fichier depuis l'application web (bouton "Exporter CSV")
  2. Placez-le dans le même dossier que ce script
  3. Lancez : python dashboard.py [fichier.csv]

Si aucun fichier n'est fourni, le script cherche le dernier
suivi_creches_*.csv dans le dossier courant.
"""

import csv, glob, os, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

STATUTS_ORDER = [
    'Non contacté', 'Email envoyé', 'Intéressé',
    'Répondu +', 'Liste attente', 'Refusé', 'Visite',
]

def find_csv():
    pattern = 'suivi_creches_*.csv'
    files = sorted(glob.glob(pattern))
    if files:
        return files[-1]
    if os.path.exists('suivi_creches.csv'):
        return 'suivi_creches.csv'
    return None

def load(path):
    rows = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    return rows

def show(rows):
    total = len(rows)
    by_statut = defaultdict(list)
    for r in rows:
        by_statut[r.get('Statut','Non contacté')].append(r)

    print('=' * 60)
    print(f"  TABLEAU DE BORD — {total} crèches")
    print('=' * 60)

    for statut in STATUTS_ORDER:
        items = by_statut.get(statut, [])
        if not items:
            continue
        bar = '█' * len(items)
        pct = len(items) / total * 100
        print(f"\n  {statut.upper():<18} {len(items):>2}  ({pct:4.0f} %)  {bar}")
        for r in sorted(items, key=lambda x: x.get('Commune','')+x.get('Nom','')):
            tel  = '📞' if r.get('Tel')=='Oui' else '  '
            note = f"  ↳ {r['Note'][:60]}" if r.get('Note','').strip() else ''
            print(f"    {tel}  {r.get('Nom','?')[:45]:<45}  {r.get('Commune','')}{note}")

    print()
    print('─' * 60)
    with_email = sum(1 for r in rows if r.get('Email','').strip())
    contacted  = sum(1 for r in rows if r.get('Statut','') not in ('Non contacté',''))
    replied    = sum(1 for r in rows if r.get('Statut','') in ('Intéressé','Répondu +','Liste attente'))
    tel_done   = sum(1 for r in rows if r.get('Tel')=='Oui')

    print(f"  Avec email       : {with_email} / {total}")
    print(f"  Contactées       : {contacted} / {total}")
    print(f"  Avec réponse     : {replied}")
    print(f"  Contactées tél.  : {tel_done}")
    print()

    # Crèches à relancer (email_envoye mais pas de réponse)
    to_follow = [r for r in rows if r.get('Statut')=='Email envoyé']
    if to_follow:
        print(f"  ⚠  À relancer ({len(to_follow)}) :")
        for r in sorted(to_follow, key=lambda x: x.get('Nom','')):
            print(f"     · {r.get('Nom','?')[:50]}")

    print()


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else find_csv()
    if not path or not os.path.exists(path):
        print("Aucun fichier suivi_creches_*.csv trouvé.")
        print("Exportez d'abord depuis l'application web (bouton 📥 Exporter CSV).")
        sys.exit(1)
    print(f"  Fichier : {path}\n")
    show(load(path))
