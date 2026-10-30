# -*- coding: utf-8 -*-
"""
Authentification Gmail OAuth2 — à lancer une seule fois.

  1. Télécharge credentials.json (client OAuth « Application de bureau »)
     depuis Google Cloud Console et place-le dans ce dossier.
  2. Lance : py gmail_auth.py
  3. Connecte-toi dans le navigateur → token.json est généré.
"""

import os, sys
from google_auth_oauthlib.flow import InstalledAppFlow

sys.stdout.reconfigure(encoding='utf-8')

SCOPES           = ['https://www.googleapis.com/auth/gmail.send',
                    'https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE       = 'token.json'

if not os.path.exists(CREDENTIALS_FILE):
    sys.exit(f"✗ {CREDENTIALS_FILE} introuvable — télécharge-le depuis Google Cloud Console.")

flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
creds = flow.run_local_server(port=0)
with open(TOKEN_FILE, 'w') as f:
    f.write(creds.to_json())
print(f"✓ {TOKEN_FILE} généré.")
