import os
import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime
from google.oauth2.service_account import Credentials

# === SETUP GOOGLE SHEETS ===

def get_gsheet_client():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file('service_account.json', scopes=scope)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Errore nell'autenticazione: {e}")
        return None


def save_vote_to_gsheet(voter, votes_with_scores):
    try:
        gc = get_gsheet_client()
        if not gc:
            return False, "Errore di autenticazione con Google"

        sheet = gc.open("Voti Ideone Bohinj 2025").worksheet("Risposte")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Preparare la riga da inserire nel foglio: [timestamp, votante, idea1, punteggio1, idea2, punteggio2, idea3, punteggio3]
        row = [timestamp, voter]
        for vote in votes_with_scores:
            row.append(vote["idea"])
            row.append(vote["punteggio"])

        result = sheet.append_row(row, value_input_option="USER_ENTERED")
        # Se il risultato è un oggetto Response, solleva errore esplicito
        if hasattr(result, 'status_code'):
            raise Exception(f"Errore API Google Sheets: {result}")
        return True, ""
    except Exception as e:
        return False, str(e)

# === CARICAMENTO IDEE ===

@st.cache_data
def load_ideas():
    df = pd.read_csv("wic_ideas.csv")
    df["Autori"] = df["Autori"].apply(lambda x: [a.strip() for a in x.split(",")])
    return df

# === INTERFACCIA ===

st.title("🧠 Concorso 'Idee di Merda' – Bohinj 2025")

try:
    df = load_ideas()
    nomi_amici = sorted(set(autore for autori in df["Autori"] for autore in autori))

    voter = st.selectbox("Chi sei?", options=nomi_amici)

    if voter:
        st.subheader("Vota le 3 idee più sceme (non puoi votare le tue)")

        own_ideas = df[df["Autori"].apply(lambda autori: voter in autori)].index
        eligible_ideas = df.drop(index=own_ideas)
        
        # Lista delle idee da votare
        idea_options = list(eligible_ideas["Idea"])
        
        st.write("### Assegna i tuoi punteggi:")
        st.write("- 3 punti = La più divertente")
        st.write("- 2 punti = La seconda più divertente")
        st.write("- 1 punto = La terza più divertente")
        
        first_choice = st.selectbox("🥇 3 punti - Prima scelta", 
                                   options=[""] + idea_options)
                                   
        # Filtra le opzioni per la seconda scelta
        second_options = [idea for idea in idea_options if idea != first_choice]
        second_choice = st.selectbox("🥈 2 punti - Seconda scelta", 
                                    options=[""] + second_options)
        
        # Filtra le opzioni per la terza scelta
        third_options = [idea for idea in idea_options 
                       if idea != first_choice and idea != second_choice]
        third_choice = st.selectbox("🥉 1 punto - Terza scelta", 
                                   options=[""] + third_options)
        
        if st.button("Invia il voto"):
            if not first_choice or not second_choice or not third_choice:
                st.error("Devi selezionare tre idee diverse.")
            else:
                # Crea un dizionario con i punteggi
                votes_with_scores = [
                    {"idea": first_choice, "punteggio": 3},
                    {"idea": second_choice, "punteggio": 2},
                    {"idea": third_choice, "punteggio": 1}
                ]
                
                success, error_msg = save_vote_to_gsheet(voter, votes_with_scores)
                if success:
                    st.success("Voto registrato con successo! 🎉")
                    st.balloons()
                else:
                    st.error(f"Errore durante il salvataggio: {error_msg}")
except Exception as e:
    st.error(f"Si è verificato un errore: {e}")
