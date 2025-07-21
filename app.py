import streamlit as st
import pandas as pd
from datetime import datetime

# Carica le idee dal file CSV
@st.cache_data
def load_ideas():
    df = pd.read_csv("idee.csv")
    df["Autori"] = df["Autori"].apply(lambda x: [a.strip() for a in x.split(",")])
    return df

# Salva i voti in un file CSV
import gspread
import json

def save_vote_to_gsheet(voter, votes):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Carica le credenziali dal secret
    credentials = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    gc = gspread.service_account_from_dict(credentials)

    # Apri il Google Sheet (sostituisci con il tuo vero ID)
    sh = gc.open_by_key("1bA8dfJcX...")  # 👈 cambia con il tuo ID reale
    worksheet = sh.sheet1

    # Salva ogni voto come una riga
    for idea_id, points in votes.items():
        worksheet.append_row([now, voter, idea_id, points])

st.set_page_config(page_title="Concorso Idee di Merda", page_icon="💩")
st.title("💩 Concorso Idee di Merda 2025")

st.markdown("""
Benvenuto! Vota le idee di merda più memorabili del campeggio, **ma non barare**: non puoi votare le tue.
Scegli **3 idee diverse** e assegna **3, 2, 1 punti**.
""")

# Carica le idee
df = load_ideas()

# Seleziona votante
voter = st.text_input("Il tuo nome (deve combaciare con gli autori)")

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
            save_vote(voter, votes)
            st.success("Voto inviato! Grazie per aver contribuito alla gloria delle peggiori idee ✨")
