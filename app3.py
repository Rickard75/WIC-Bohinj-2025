import os
import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime
from google.oauth2.service_account import Credentials

# === SETUP GOOGLE SHEETS ===

def get_gsheet_client():
    credentials_dict = st.secrets["gcp_service_account"]
    credentials_json = json.dumps(credentials_dict)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_json_keyfile_dict(json.loads(credentials_json), scope)
    return gspread.authorize(credentials)

def save_vote_to_gsheet(voter, votes):
    gc = get_gsheet_client()
    sheet = gc.open("Voti Ideone Bohinj 2025").worksheet("Risposte")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, voter] + votes
    sheet.append_row(row)

# === CARICAMENTO IDEE ===

@st.cache_data
def load_ideas():
    df = pd.read_csv("wic_ideas.csv")
    df["Autori"] = df["Autori"].apply(lambda x: [a.strip() for a in x.split(",")])
    return df

# === INTERFACCIA ===

st.title("🧠 Concorso 'Idee di Merda' – Bohinj 2025")

df = load_ideas()
nomi_amici = sorted(set(autore for autori in df["Autori"] for autore in autori))

voter = st.selectbox("Chi sei?", options=nomi_amici)

if voter:
    st.subheader("Vota le 3 idee più sceme (non puoi votare le tue)")

    own_ideas = df[df["Autori"].apply(lambda autori: voter in autori)].index
    eligible_ideas = df.drop(index=own_ideas)

    selected = st.multiselect(
        "Scegli 3 idee che ti hanno fatto più ridere (escludi le tue)",
        eligible_ideas["Titolo"],
        max_selections=3
    )

    if st.button("Invia il voto"):
        if len(selected) != 3:
            st.error("Devi selezionare esattamente 3 idee.")
        else:
            save_vote_to_gsheet(voter, selected)
            st.success("Voto registrato con successo! 🎉")
