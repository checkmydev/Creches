# -*- coding: utf-8 -*-
"""
Envoi automatique des demandes d'inscription en crèche.

AVANT D'ENVOYER :
  1. Activez la validation en 2 étapes sur votre compte Google :
       https://myaccount.google.com/security
  2. Créez un Mot de passe d'application (16 caractères) :
       https://myaccount.google.com/apppasswords
       → Catégorie : "Autre" → nommez-le "Crèches"
  3. Collez ce mot de passe dans SMTP_PASSWORD ci-dessous.
  4. Mettez DRY_RUN = False pour envoyer réellement.
"""

import csv, smtplib, sys, uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION  (à compléter avant envoi)
# ═══════════════════════════════════════════════════════════
DRY_RUN       = False  # ← True : aucun envoi, affiche seulement la liste
TEST_MODE     = True   # ← True : envoie TOUT à SMTP_USER (test personnel, aucun vrai destinataire)
SMTP_USER     = 'maxime.gerard.be@gmail.com'
SMTP_PASSWORD = 'djcx jlxa bbdi abjq'   # 16 caractères, sans espaces
CC_EMAIL      = 'cortvrintm@gmail.com'
CSV_FILE      = 'creches_moins_20km_limelette.csv'
# ═══════════════════════════════════════════════════════════

SUBJECT = "Demande d'inscription – naissance attendue le 18 janvier 2027"

# ── Corps du mail ──────────────────────────────────────────
# {INTRO_CRECHE} est remplacé selon qu'il y a une ou plusieurs crèches.
BODY_TEMPLATE = """\
Madame, Monsieur,

Nous nous permettons de vous contacter afin de vous adresser une demande \
d'inscription anticipée pour notre futur enfant, dont la naissance est \
attendue le 18 janvier 2027.

Nous sommes Maxime Gerard et Marie Cortvrint, résidant au :
  Avenue Lambermont 53
  1342 Limelette

Nous souhaitons confier notre enfant {INTRO_CRECHE} à partir du 1er mai 2027, \
soit environ trois mois et demi après la naissance. Ce délai correspond à la \
fin du congé de maternité/paternité et marque le moment où nous devrons tous \
deux reprendre nos activités professionnelles.

Votre établissement correspond tout particulièrement à nos critères de \
proximité et nous avons entendu de très bons retours à son sujet. C'est la \
raison pour laquelle {NOM_COURT} figure en tête de nos préférences.

Pourriez-vous nous indiquer :
  – la procédure à suivre pour formaliser cette préinscription,
  – les documents à nous fournir dès à présent ou après la naissance,
  – les disponibilités éventuelles pour une entrée au 1er mai 2027,
  – si vous organisez des visites de votre structure ?

Nous restons bien entendu disponibles pour tout renseignement complémentaire \
et nous tenons à votre disposition pour convenir d'un rendez-vous selon vos \
disponibilités.

Dans l'attente de votre réponse, nous vous adressons nos cordiales salutations.

Maxime Gerard & Marie Cortvrint
Avenue Lambermont 53 — 1342 Limelette
Tél. Maxime : 0473/77.35.86
Tél. Marie  : 0496/11.27.83
Email       : maxime.gerard.be@gmail.com / cortvrintm@gmail.com
"""


def build_body(noms):
    """Adapte le corps selon qu'une ou plusieurs crèches partagent l'email."""
    if len(noms) == 1:
        intro   = f"à {noms[0]}"
        court   = noms[0]
    else:
        liste   = ", ".join(noms[:-1]) + f" et {noms[-1]}"
        intro   = f"à l'une des crèches que vous gérez ({liste})"
        # nom court = préfixe commun ou 1er nom
        court   = noms[0]
    return BODY_TEMPLATE.replace('{INTRO_CRECHE}', intro).replace('{NOM_COURT}', court)


def send_email(to_email, noms):
    body = build_body(noms)

    # En mode test, on redirige vers soi-même et on ajoute un bandeau d'info
    if TEST_MODE:
        actual_to = SMTP_USER
        actual_cc = None
        prefix = (
            f"[TEST — destinataire réel : {to_email}]\n"
            f"[Creche(s) : {', '.join(noms)}]\n\n"
        )
        subject = f"[TEST] {noms[0]} — {SUBJECT}"
    else:
        actual_to = to_email
        actual_cc = CC_EMAIL
        prefix    = ''
        subject   = SUBJECT

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
        if TEST_MODE:
            print(f"  ✓ [TEST] Envoyé à {actual_to} (pour {', '.join(noms)})")
        else:
            print(f"  ✓ Envoyé → {', '.join(noms)} <{to_email}>")
        return True
    except Exception as e:
        print(f"  ✗ ERREUR → {to_email} : {e}")
        return False


# ── Lecture du CSV et regroupement par email ───────────────
groups = defaultdict(list)
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        email = row['Email'].strip()
        nom   = row['Nom'].strip()
        if email:
            # Évite les doublons de nom (ex : 2× "La Ribambelle" même email)
            if nom not in groups[email]:
                groups[email].append(nom)

total = len(groups)
if DRY_RUN:
    mode_label = "DRY RUN — aucun email ne sera envoyé"
elif TEST_MODE:
    mode_label = f"TEST — tous les emails arrivent dans votre boîte ({SMTP_USER})"
else:
    mode_label = "ENVOI RÉEL vers les crèches"

print("=" * 60)
print(f"  MODE : {mode_label}")
print(f"  Destinataires uniques : {total}")
print("=" * 60)
print()

ok = fail = 0
for email, noms in sorted(groups.items()):
    if send_email(email, noms):
        ok += 1
    else:
        fail += 1

print("─" * 60)
print(f"Résultat : {ok} OK  |  {fail} erreur(s)")
if DRY_RUN:
    print()
    print("→ Étapes suivantes :")
    print("  1. Créez un App Password Google (voir commentaire en tête de fichier)")
    print("  2. Renseignez SMTP_PASSWORD")
    print("  3. TEST_MODE = True  + DRY_RUN = False  → reçoit tout dans votre boîte")
    print("  4. TEST_MODE = False + DRY_RUN = False  → envoi réel aux crèches")
