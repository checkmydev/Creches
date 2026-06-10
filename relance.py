# -*- coding: utf-8 -*-
"""
Envoi des emails de relance aux crèches qui n'ont pas répondu.

Critères : statut == "Email envoyé" dans le CSV de suivi exporté depuis
           l'application web.

Usage :
  1. Exportez le suivi depuis l'appli web (bouton 📥 Exporter CSV)
  2. Renseignez SMTP_PASSWORD et pointez SUIVI_CSV vers ce fichier
  3. Ajustez DELAI_MIN_JOURS si besoin (défaut : 14 jours)
  4. Lancez : python relance.py

Modes :
  DRY_RUN  = True  → affiche la liste sans envoyer
  TEST_MODE = True → envoie tout à SMTP_USER (test personnel)
"""

import csv, smtplib, sys, uuid, glob, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
DRY_RUN       = True
TEST_MODE     = True
SMTP_USER     = 'maxime.gerard.be@gmail.com'
SMTP_PASSWORD = ''            # ← Google App Password (16 car.)
CC_EMAIL      = 'cortvrintm@gmail.com'
SUIVI_CSV     = ''            # ← laisser vide pour auto-détection
# ═══════════════════════════════════════════════════════════

SUBJECT_RELANCE = "Relance — Demande d'inscription – naissance attendue le 18 janvier 2027"

BODY_RELANCE = """\
Madame, Monsieur,

Nous nous permettons de vous contacter à nouveau suite à notre demande \
d'inscription anticipée envoyée il y a quelques semaines.

Nous sommes Maxime Gerard et Marie Cortvrint et nous attendons un enfant \
pour le 18 janvier 2027. Nous souhaitons l'inscrire {INTRO_CRECHE} \
à partir du 1er mai 2027.

Si vous n'avez pas eu l'occasion de répondre à notre premier message, \
nous serions très reconnaissants de pouvoir recevoir votre retour \
concernant les éventuelles disponibilités ou la procédure d'inscription.

Nous restons bien entendu disponibles pour tout renseignement \
complémentaire.

Dans l'attente de votre réponse, nous vous adressons nos cordiales \
salutations.

Maxime Gerard & Marie Cortvrint
Avenue Lambermont 53 — 1342 Limelette
Tél. Maxime : 0473/77.35.86
Tél. Marie  : 0496/11.27.83
Email       : maxime.gerard.be@gmail.com / cortvrintm@gmail.com
"""


def build_body(noms):
    if len(noms) == 1:
        intro = f"à {noms[0]}"
    else:
        liste = ", ".join(noms[:-1]) + f" et {noms[-1]}"
        intro = f"à l'une des crèches que vous gérez ({liste})"
    return BODY_RELANCE.replace('{INTRO_CRECHE}', intro)


def find_suivi():
    files = sorted(glob.glob('suivi_creches_*.csv'))
    if files:
        return files[-1]
    if os.path.exists('suivi_creches.csv'):
        return 'suivi_creches.csv'
    return None


def send_relance(to_email, noms):
    body = build_body(noms)

    if TEST_MODE:
        actual_to = SMTP_USER
        actual_cc = None
        prefix    = f"[TEST — destinataire réel : {to_email}]\n[Crèche(s) : {', '.join(noms)}]\n\n"
        subject   = f"[RELANCE TEST] {noms[0]} — {SUBJECT_RELANCE}"
    else:
        actual_to = to_email
        actual_cc = CC_EMAIL
        prefix    = ''
        subject   = SUBJECT_RELANCE

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


csv_path = SUIVI_CSV or find_suivi()
if not csv_path or not os.path.exists(csv_path):
    print("Aucun fichier de suivi trouvé.")
    print("Exportez d'abord depuis l'application web puis relancez ce script.")
    sys.exit(1)

print(f"  Fichier suivi : {csv_path}\n")

groups = defaultdict(list)
with open(csv_path, newline='', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        if row.get('Statut','') == 'Email envoyé' and row.get('Email','').strip():
            email = row['Email'].strip()
            nom   = row['Nom'].strip()
            if nom not in groups[email]:
                groups[email].append(nom)

total = len(groups)
if total == 0:
    print("Aucune crèche à relancer (statut 'Email envoyé' avec une adresse email).")
    sys.exit(0)

if DRY_RUN:
    mode_label = "DRY RUN — aucun email ne sera envoyé"
elif TEST_MODE:
    mode_label = f"TEST — tous les emails arrivent dans votre boîte ({SMTP_USER})"
else:
    mode_label = "ENVOI RÉEL des relances"

print('=' * 60)
print(f"  MODE : {mode_label}")
print(f"  Destinataires à relancer : {total}")
print('=' * 60)
print()

ok = fail = 0
for email, noms in sorted(groups.items()):
    if send_relance(email, noms):
        ok += 1
    else:
        fail += 1

print('─' * 60)
print(f"Résultat : {ok} OK  |  {fail} erreur(s)")
