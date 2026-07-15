# -*- coding: utf-8 -*-
"""
Envoi automatique des demandes d'inscription en crèche via Gmail API OAuth2.

AVANT D'ENVOYER :
  1. Lance gmail_auth.py une seule fois pour générer token.json.
  2. Mets DRY_RUN = False pour envoyer réellement.
"""

import csv, base64, sys, uuid, os, time, json, urllib.request, datetime
from dotenv import load_dotenv
load_dotenv()
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from collections import defaultdict

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
DRY_RUN       = False  # ← True : aucun envoi, affiche seulement la liste
TEST_MODE     = False  # ← True : envoie TOUT à GMAIL_USER (test personnel)
GMAIL_USER    = 'maxime.gerard.be@gmail.com'
CC_EMAIL      = 'cortvrintm@gmail.com'
CSV_FILE      = 'creches_moins_20km_limelette.csv'
ATTACHMENT    = 'Certificat.jfif'   # Certificat de grossesse joint au mail
# Laisser vide [] pour envoyer à tous les types
# Types possibles : 'CPAS', 'Communale', 'Parentale', 'Accueillante', 'Privée'
TYPE_FILTER   = ['Privée']
# Laisser vide [] pour envoyer à tous les emails du type ; sinon whitelist d'emails exacts
EMAIL_WHITELIST = []  # Laisser vide pour envoyer à tous les emails du type
SUPABASE_URL  = 'https://wzrcrszfubjsfoaxatvo.supabase.co'
SUPABASE_KEY  = os.environ.get('SUPABASE_SERVICE_KEY', '')
# ═══════════════════════════════════════════════════════════

SCOPES         = ['https://www.googleapis.com/auth/gmail.send',
                  'https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE       = 'token.json'
# ═══════════════════════════════════════════════════════════

SUBJECT = "Demande d'inscription – naissance attendue le 16 janvier 2027"

# ── Corps du mail ──────────────────────────────────────────
# {INTRO_CRECHE} est remplacé selon qu'il y a une ou plusieurs crèches.
BODY_TEMPLATE = """\
Madame, Monsieur,

Nous nous permettons de vous contacter afin de vous adresser une demande \
d'inscription anticipée pour notre futur enfant, dont la naissance est \
attendue le 16 janvier 2027.

Nous sommes Maxime Gerard et Marie Cortvrint, résidant au :
  Avenue Lambermont 53
  1342 Limelette

Nous souhaitons confier notre enfant {INTRO_CRECHE} à partir du 1er juin 2027, \
soit environ quatre mois et demi après la naissance. Ce délai correspond à la \
fin du congé de maternité/paternité et marque le moment où nous devrons tous \
deux reprendre nos activités professionnelles.

Votre établissement correspond tout particulièrement à nos critères de \
proximité et nous avons entendu de très bons retours à son sujet. C'est la \
raison pour laquelle {NOM_COURT} figure en tête de nos préférences.

Vous trouverez en pièce jointe notre certificat de grossesse.

Pourriez-vous nous indiquer :
  – la procédure à suivre pour formaliser cette préinscription,
  – les documents à nous fournir dès à présent ou après la naissance,
  – les disponibilités éventuelles pour une entrée au 1er juin 2027,
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


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError('token.json manquant ou invalide — lance gmail_auth.py d\'abord.')
    return build('gmail', 'v1', credentials=creds)


def supabase_mark_sent(noms):
    """Met le statut 'email_envoye' dans Supabase pour les crèches sans statut."""
    if DRY_RUN or TEST_MODE:
        return
    url = f"{SUPABASE_URL}/rest/v1/suivi_creches"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal',
    }
    today = datetime.date.today().isoformat()
    rows = [{'nom': n, 'statut': 'email_envoye', 'tel': False, 'note': '', 'date_envoi': today} for n in noms]
    data = json.dumps(rows).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  ⚠ Supabase non mis à jour : {e}")


def detect_type(nom):
    n = nom.lower()
    if 'cpas' in n:         return 'CPAS'
    if 'accueillante' in n: return 'Accueillante'
    if 'parentale' in n:    return 'Parentale'
    if 'communale' in n or 'communal' in n: return 'Communale'
    return 'Privée'


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


def send_email(service, to_email, noms):
    body = build_body(noms)

    if TEST_MODE:
        actual_to = GMAIL_USER
        actual_cc = CC_EMAIL
        prefix    = (f"[TEST — destinataire réel : {to_email}]\n"
                     f"[Creche(s) : {', '.join(noms)}]\n\n")
        subject   = f"[TEST] {noms[0]} — {SUBJECT}"
    else:
        actual_to = to_email
        actual_cc = CC_EMAIL
        prefix    = ''
        subject   = SUBJECT

    msg = MIMEMultipart()
    msg['From']       = GMAIL_USER
    msg['To']         = actual_to
    if actual_cc:
        msg['Cc']     = actual_cc
    msg['Subject']    = subject
    msg['Message-ID'] = f"<{uuid.uuid4()}@creches.local>"
    msg.attach(MIMEText(prefix + body, 'plain', 'utf-8'))

    if os.path.exists(ATTACHMENT):
        with open(ATTACHMENT, 'rb') as f:
            part = MIMEBase('image', 'jpeg')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='Certificat_grossesse.jpg')
        msg.attach(part)

    if DRY_RUN:
        print(f"  À    : {actual_to if TEST_MODE else to_email}")
        if not TEST_MODE:
            print(f"  CC   : {CC_EMAIL}")
        print(f"  Pour : {', '.join(noms)}")
        print()
        return True

    try:
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId='me', body={'raw': raw}).execute()
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
            if TYPE_FILTER and detect_type(nom) not in TYPE_FILTER:
                continue
            if EMAIL_WHITELIST and email not in EMAIL_WHITELIST:
                continue
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

service = None if DRY_RUN else get_gmail_service()

ok = fail = 0
for email, noms in sorted(groups.items()):
    if send_email(service, email, noms):
        ok += 1
        supabase_mark_sent(noms)
        if not DRY_RUN:
            time.sleep(3)
    else:
        fail += 1
        if not DRY_RUN:
            time.sleep(5)

print("─" * 60)
print(f"Résultat : {ok} OK  |  {fail} erreur(s)")
if DRY_RUN:
    print()
    print("→ Étapes suivantes :")
    print("  1. Lance gmail_auth.py pour générer token.json")
    print("  2. TEST_MODE = True  + DRY_RUN = False  → reçoit tout dans ta boîte")
    print("  3. TEST_MODE = False + DRY_RUN = False  → envoi réel aux crèches")
