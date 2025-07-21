import json
import gspread
from google.oauth2.service_account import Credentials

# Carica le credenziali
with open('service_account.json') as f:
    credentials_json = json.load(f)

# Configurazione credenziali
scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(credentials_json, scopes=scopes)
gc = gspread.authorize(creds)

# Verifica accesso al foglio
try:
    SHEET_ID = "1l25oan06keM5VgHU7cpdknOIMk7wzCjWBJ0picuHvmQ"
    sh = gc.open_by_key(SHEET_ID)
    print(f"Accesso riuscito! Il foglio si chiama: {sh.title}")
except Exception as e:
    print(f"Errore: {e}")
    print("Controlla l'ID del foglio e assicurati che sia condiviso con:", credentials_json.get("client_email", "email non trovata"))