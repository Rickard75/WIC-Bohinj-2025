import os
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
import json
from google.oauth2.service_account import Credentials

# Carica le idee dal file CSV
@st.cache_data
def load_ideas():
    df = pd.read_csv("wic_ideas.csv")  # Corretto nome del file
    df["Autori"] = df["Autori"].apply(lambda x: [a.strip() for a in x.split(",")])
    return df

# Salva i voti in un file CSV
def save_vote_to_gsheet(voter, votes):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Carica le credenziali dal file JSON con percorso assoluto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    service_account_path = os.path.join(script_dir, 'service_account.json')
    
    with open(service_account_path) as f:
        credentials_json = json.load(f)
    
    # Configurazione delle credenziali con gli scope necessari
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(credentials_json, scopes=scopes)
    gc = gspread.authorize(creds)
    
    # Apri il Google Sheet (sostituisci con il tuo vero ID)
    SHEET_ID = "1l25oan06keM5VgHU7cpdknOIMk7wzCjWBJ0picuHvmQ"  # Sostituisci con l'ID del tuo foglio
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1

    # Salva ogni voto come una riga
    for idea_id, points in votes.items():
        worksheet.append_row([now, voter, idea_id, points])

# Configurazione della pagina
st.set_page_config(page_title="Concorso Idee di Merda", page_icon="💩")
st.title("💩 Concorso Idee di Merda 2025")

st.markdown("""
Benvenuto! Vota le idee di merda più memorabili del campeggio, **ma non barare**: non puoi votare le tue.
Scegli **3 idee diverse** e assegna **3, 2, 1 punti**.
""")

# Carica le idee
df = load_ideas()

# Seleziona votante
votanti = ["Rick", "Cappio", "Coach", "Fra", "Bruce", "Andre", "Giada", "Lanny "]
voter = st.selectbox("Chi sei?", votanti)

if voter:
    # Filtra idee che NON sono dell'utente
    filtered_df = df[~df["Autori"].apply(lambda autori: voter in autori)]

    if filtered_df.empty:
        st.warning("Hai proposto tutte le idee? Non puoi votare nessuna allora! 💀")
    else:
        st.markdown("## Seleziona 3 idee diverse e assegna i punti")

        options = filtered_df[["ID", "Idea"]].values.tolist()
        options_display = [f"{idea}" for _, idea in options]
        idea_map = {idea: id_ for id_, idea in options}

        choice_3 = st.selectbox("3 Punti a...", options_display, key="3")
        remaining_2 = [opt for opt in options_display if opt != choice_3]
        choice_2 = st.selectbox("2 Punti a...", remaining_2, key="2")
        remaining_1 = [opt for opt in remaining_2 if opt != choice_2]
        choice_1 = st.selectbox("1 Punto a...", remaining_1, key="1")

        if st.button("Invia voto"):
            votes = {
                idea_map[choice_3]: 3,
                idea_map[choice_2]: 2,
                idea_map[choice_1]: 1,
            }
            save_vote_to_gsheet(voter, votes)
            st.success("Voto inviato! Grazie per aver contribuito alla gloria delle peggiori idee ✨")