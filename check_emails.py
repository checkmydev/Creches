# -*- coding: utf-8 -*-
"""
Vérification SMTP des adresses email sans envoyer de message.

Utilise la commande RCPT TO pour tester si chaque adresse est valide
auprès du serveur de destination.

Note : certains serveurs acceptent tout (greylisting, catch-all) —
       un résultat "OK" ne garantit pas la délivrabilité à 100 %.
       Un résultat "KO" indique presque toujours une adresse invalide.

Usage : python check_emails.py
"""

import csv, smtplib, socket, sys, time
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

CSV_FILE    = 'creches_moins_20km_limelette.csv'
FROM_EMAIL  = 'maxime.gerard.be@gmail.com'
PAUSE_SEC   = 1.5   # délai entre chaque serveur pour éviter le rate-limiting

def check_address(email):
    domain = email.split('@')[-1]
    try:
        import dns.resolver
        records = dns.resolver.resolve(domain, 'MX')
        mx = sorted(records, key=lambda r: r.preference)[0].exchange.to_text().rstrip('.')
    except Exception:
        mx = domain

    try:
        with smtplib.SMTP(mx, 25, timeout=10) as srv:
            srv.ehlo_or_helo_if_needed()
            srv.mail(FROM_EMAIL)
            code, msg = srv.rcpt(email)
            return code, msg.decode(errors='replace')
    except smtplib.SMTPRecipientsRefused as e:
        code, msg = list(e.recipients.values())[0]
        return code, msg.decode(errors='replace')
    except smtplib.SMTPConnectError as e:
        return 0, f"Connexion refusée : {e}"
    except socket.timeout:
        return 0, "Timeout"
    except Exception as e:
        return 0, str(e)


# Lire les emails uniques depuis le CSV
emails = {}
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        email = row.get('Email','').strip()
        nom   = row.get('Nom','').strip()
        if email and email not in emails:
            emails[email] = nom

print('=' * 65)
print(f"  Vérification de {len(emails)} adresses email uniques")
print(f"  Source MX : résolution DNS directe (port 25)")
print('=' * 65)
print()

has_dns = True
try:
    import dns.resolver
except ImportError:
    has_dns = False
    print("⚠  Module 'dnspython' non installé — résolution MX désactivée.")
    print("   Installez-le : pip install dnspython")
    print("   Sans lui, le script tente smtp.<domaine> (moins fiable).\n")

ok_list   = []
fail_list = []

for i, (email, nom) in enumerate(sorted(emails.items()), 1):
    code, msg = check_address(email)
    ok = (200 <= code < 300)
    symbol = '✓' if ok else '✗'
    status = 'OK' if ok else f'KO ({code})'
    short  = msg[:60].strip()
    print(f"  {symbol}  [{i:>2}/{len(emails)}]  {email:<40}  {status}")
    if not ok:
        print(f"       └─ {short}")
        fail_list.append((email, nom, code, short))
    else:
        ok_list.append((email, nom))
    time.sleep(PAUSE_SEC)

print()
print('─' * 65)
print(f"  Valides : {len(ok_list)}    Invalides / erreurs : {len(fail_list)}")
print()

if fail_list:
    print("  Adresses à vérifier manuellement :")
    for email, nom, code, msg in fail_list:
        print(f"    · {email}  ({nom})  — {code} {msg}")
    print()
