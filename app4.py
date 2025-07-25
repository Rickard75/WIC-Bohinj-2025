import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# === CONFIGURAZIONE GOOGLE SHEETS ===
# Path al file di credenziali JSON (deve essere nella stessa directory o specificato correttamente)
GSHEET_CREDENTIALS_PATH = "service_account.json"  # Cambia con il tuo nome file se diverso
GSHEET_NAME = "Voti WIC Bohinj 2025"  # Nome del tuo foglio Google

# === FUNZIONE PER CONNETTERSI A GOOGLE SHEETS ===
@st.cache_resource
#def get_gsheet_client():
#    creds = Credentials.from_service_account_file(
#        GSHEET_CREDENTIALS_PATH,
#        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
#    )
#    return gspread.authorize(creds)

def get_gsheet_client2():
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)


# === FUNZIONE PER SALVARE I VOTI NEL FOGLIO ===
def save_vote_to_gsheet(username, voto1, voto2, voto3, df):
    try:
        client = get_gsheet_client2()
        sheet = client.open(GSHEET_NAME).sheet1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Crea le righe da scrivere: ogni riga è (timestamp, utente, idea, autori, punteggio)
        def get_autori(idea_text):
            autori = df[df["Idea"] == idea_text]["Autori"].values
            return ", ".join(autori[0]) if autori.size > 0 else "Sconosciuto"

        rows = [
            [now, username, voto1, get_autori(voto1), 3],
            [now, username, voto2, get_autori(voto2), 2],
            [now, username, voto3, get_autori(voto3), 1]
        ]

        # Scrive tutte le righe in una volta
        for row in rows:
            sheet.append_row(row)

        st.success("✅ Voto registrato con successo!")
    except Exception as e:
        st.error(f"❌ Errore durante il salvataggio: {e}")

# === CARICA IL FILE CON LE IDEE ===
@st.cache_data
def load_ideas(filepath="wic_ideas.csv"):
    df = pd.read_csv(filepath, header=None, names=["ID", "Idea", "Autori"])
    # Converte "Mario, Anna" → ["Mario", "Anna"]
    df["Autori"] = df["Autori"].apply(lambda x: [a.strip() for a in x.split(",")])
    return df

# === INTERFACCIA DELL'APP ===
def main():
    st.title("💩 Idee di Merda – Bohinj 2025")
    st.markdown("""
    Vota le idee più divertenti, folli, assurde.  
    **Non puoi votare le tue.**  
    Dai 3 punti alla più "bella", 2 alla seconda, 1 alla terza.
    """)

    df = load_ideas()

    # Lista di tutti gli autori (unici)
    autori_unici = sorted(set(sum(df["Autori"].tolist(), [])))

    # Seleziona utente
    username = st.selectbox("Chi sei?", autori_unici)

    # Filtra le idee: rimuove quelle dove compare lo user tra gli autori
    idee_votabili = df[~df["Autori"].apply(lambda autori: username in autori)]

    # Mostra tre dropdown per votare
    st.subheader("Scegli le tue 3 idee preferite (senza ripetizioni)")
    idee_opzioni = idee_votabili["Idea"].tolist()

    voto1 = st.selectbox("🥇 Primo posto (3 punti)", [""] + idee_opzioni)
    voto2 = st.selectbox("🥈 Secondo posto (2 punti)", [""] + [idea for idea in idee_opzioni if idea != voto1])
    voto3 = st.selectbox("🥉 Terzo posto (1 punto)", [""] + [idea for idea in idee_opzioni if idea not in [voto1, voto2]])

    # Bottone di invio
    if st.button("✅ Invia il tuo voto"):
        if not voto1 or not voto2 or not voto3:
            st.error("Devi scegliere 3 idee diverse.")
        else:
            try:
                save_vote_to_gsheet(username, voto1, voto2, voto3, df)
                st.success("Voto registrato con successo!")
            except Exception as e:
                st.error(f"Errore durante il salvataggio: {e}")

# === ESECUZIONE ===
if __name__ == "__main__":
    main()
