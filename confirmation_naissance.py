# -*- coding: utf-8 -*-
"""
Email de confirmation post-naissance aux crèches ayant répondu positivement.

À envoyer après la naissance pour confirmer l'inscription et communiquer
le prénom et la date exacte de naissance.

Critères : statut == "Répondu +" dans le CSV de suivi exporté depuis
           l'application web.

Usage :
  1. Renseignez PRENOM_BEBE et DATE_NAISSANCE_EXACTE ci-dessous
  2. Exportez le suivi depuis l'appli web (bouton 📥 Exporter CSV)
  3. Mettez DRY_RUN = False et TEST_MODE = False pour envoyer réellement
  4. Lancez : python confirmation_naissance.py
"""

import csv, smtplib, sys, uuid, glob, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
#  À COMPLÉTER APRÈS LA NAISSANCE
# ═══════════════════════════════════════════════════════════
PRENOM_BEBE         = ''    # ← Ex : 'Emma'
DATE_NAISSANCE      = ''    # ← Ex : 'le 18 janvier 2027'
SEXE                = 'notre enfant'  # ← 'notre fils' ou 'notre fille'

DRY_RUN             = True
TEST_MODE           = True
SMTP_USER           = 'maxime.gerard.be@gmail.com'
SMTP_PASSWORD       = ''    # ← Google App Password (16 car.)
CC_EMAIL            = 'cortvrintm@gmail.com'
SUIVI_CSV           = ''    # ← laisser vide pour auto-détection
# ═══════════════════════════════════════════════════════════

BODY_CONFIRMATION = """\
Madame, Monsieur,

Nous avons le bonheur de vous annoncer la naissance de {SEXE}, \
{PRENOM} {DATE_NAISSANCE}.

Suite à notre échange précédent concernant une inscription à \
votre crèche, nous souhaitons confirmer notre souhait de vous confier \
{PRENOM} à partir du 1er mai 2027.

Pourriez-vous nous confirmer la procédure à suivre pour finaliser \
l'inscription et nous indiquer les documents que nous devons vous fournir ?

Nous restons disponibles pour tout rendez-vous à votre convenance.

Dans l'attente de votre retour, nous vous adressons nos cordiales \
salutations.

Maxime Gerard & Marie Cortvrint
Avenue Lambermont 53 — 1342 Limelette
Tél. Maxime : 0473/77.35.86
Tél. Marie  : 0496/11.27.83
Email       : maxime.gerard.be@gmail.com / cortvrintm@gmail.com
"""


def build_subject():
    if PRENOM_BEBE:
        return f"Confirmation inscription — {PRENOM_BEBE}, né(e) {DATE_NAISSANCE}"
    return f"Confirmation inscription — naissance {DATE_NAISSANCE}"


def build_body(noms):
    prenom = PRENOM_BEBE if PRENOM_BEBE else 'notre enfant'
    date   = DATE_NAISSANCE if DATE_NAISSANCE else 'récemment'
    sexe   = SEXE if SEXE else 'notre enfant'
    body   = BODY_CONFIRMATION \
        .replace('{PRENOM}', prenom) \
        .replace('{DATE_NAISSANCE}', date) \
        .replace('{SEXE}', sexe)
    if len(noms) > 1:
        liste  = ", ".join(noms[:-1]) + f" et {noms[-1]}"
        insert = f"(concernant l'une de vos crèches : {liste})"
        body   = body.replace('votre crèche', f'votre crèche {insert}')
    return body


def find_suivi():
    files = sorted(glob.glob('suivi_creches_*.csv'))
    if files:
        return files[-1]
    if os.path.exists('suivi_creches.csv'):
        return 'suivi_creches.csv'
    return None


def send_confirmation(to_email, noms):
    body    = build_body(noms)
    subject = build_subject()

    if TEST_MODE:
        actual_to = SMTP_USER
        actual_cc = None
        prefix    = f"[TEST — destinataire réel : {to_email}]\n[Crèche(s) : {', '.join(noms)}]\n\n"
        subject   = f"[CONF TEST] {noms[0]} — {subject}"
    else:
        actual_to = to_email
        actual_cc = CC_EMAIL
        prefix    = ''

    msg = MIMEMultipart()
    msg['From']       = SMTP_USER
    msg['To']         = actual_to
    if actual_cc:
        msg['Cc']     = actual_cc
    msg['Subject']    = subject
    msg['Message-ID'] = f"<{uuid.uuid4()}@creches.local>"
    msg.attach(MIMEText(prefix + body, 'plain', 'utf-8'))

    if DRY_RUN:
        print(f"  À    : {actual_to if TEST_MODE else to_email}")
        if not TEST_MODE:
            print(f"  CC   : {CC_EMAIL}")
        print(f"  Pour : {', '.join(noms)}")
        print()
        return True

    try:
        recipients = [actual_to] + ([actual_cc] if actual_cc else [])
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as srv:
            srv.login(SMTP_USER, SMTP_PASSWORD)
            srv.sendmail(SMTP_USER, recipients, msg.as_string())
        print(f"  ✓ Envoyé → {', '.join(noms)} <{to_email}>")
        return True
    except Exception as e:
        print(f"  ✗ ERREUR → {to_email} : {e}")
        return False


if not PRENOM_BEBE and not DRY_RUN:
    print("⚠  Renseignez PRENOM_BEBE avant d'envoyer réellement.")
    sys.exit(1)

csv_path = SUIVI_CSV or find_suivi()
if not csv_path or not os.path.exists(csv_path):
    print("Aucun fichier de suivi trouvé.")
    print("Exportez d'abord depuis l'application web puis relancez ce script.")
    sys.exit(1)

print(f"  Fichier suivi : {csv_path}\n")

groups = defaultdict(list)
with open(csv_path, newline='', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        if row.get('Statut','') == 'Répondu +' and row.get('Email','').strip():
            email = row['Email'].strip()
            nom   = row['Nom'].strip()
            if nom not in groups[email]:
                groups[email].append(nom)

total = len(groups)
if total == 0:
    print("Aucune crèche avec statut 'Répondu +' et une adresse email.")
    sys.exit(0)

if DRY_RUN:
    mode_label = "DRY RUN — aucun email ne sera envoyé"
elif TEST_MODE:
    mode_label = f"TEST — tous les emails arrivent dans votre boîte ({SMTP_USER})"
else:
    mode_label = "ENVOI RÉEL des confirmations"

print('=' * 60)
print(f"  MODE     : {mode_label}")
print(f"  Bébé     : {PRENOM_BEBE or '(non renseigné)'}")
print(f"  Naissance: {DATE_NAISSANCE or '(non renseignée)'}")
print(f"  Crèches  : {total} destinataire(s)")
print('=' * 60)
print()

ok = fail = 0
for email, noms in sorted(groups.items()):
    if send_confirmation(email, noms):
        ok += 1
    else:
        fail += 1

print('─' * 60)
print(f"Résultat : {ok} OK  |  {fail} erreur(s)")
