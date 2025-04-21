%%writefile app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# === Config ===
DRIVE_PATH = "/content/drive/MyDrive/matelas_data.xlsx"
LOCAL_PATH = "/content/matelas_data.xlsx"

# === Dropdown Options ===
CLIENTS = ["Decathlon", "Benetton", "Zara", "Autre"]
TISSUS = ["Coton", "Polyester", "Élasthanne", "Autre"]

# === Init Excel File ===
def init_excel():
    if not os.path.exists(DRIVE_PATH):
        df = pd.DataFrame(columns=[
            "Date", "Client", "N° Commande", "Tissu", "Code Rouleau",
            "Longueur Matelas", "Nombre de Plis", "Heure Début", "Heure Fin", "Temps Opération"
        ])
        df.to_excel(DRIVE_PATH, index=False)
    if not os.path.exists(LOCAL_PATH):
        pd.read_excel(DRIVE_PATH).to_excel(LOCAL_PATH, index=False)

init_excel()

# === Load Existing Data ===
def load_data():
    return pd.read_excel(DRIVE_PATH)

# === Save Entry ===
def save_entry(data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(DRIVE_PATH, index=False)
    df.to_excel(LOCAL_PATH, index=False)

# === Streamlit App ===
st.set_page_config(page_title="Saisie Matelas", layout="centered")

st.markdown("<h1 style='color:green;'>Formulaire de Saisie</h1>", unsafe_allow_html=True)
st.write("Remplissez les champs suivants pour enregistrer les opérations.")

with st.form("formulaire"):
    date = st.date_input("Date")
    client = st.selectbox("Client", CLIENTS)
    commande = st.text_input("N° Commande")
    tissu = st.selectbox("Tissu", TISSUS)
    code_rouleau = st.text_input("Code Rouleau")
    longueur = st.number_input("Longueur Matelas (m)", step=0.1)
    plis = st.number_input("Nombre de Plis", step=1)
    heure_debut = st.text_input("Heure Début (HH:MM)")
    heure_fin = st.text_input("Heure Fin (HH:MM)")

    submitted = st.form_submit_button("Enregistrer")

    if submitted:
        try:
            t1 = datetime.strptime(heure_debut.strip(), "%H:%M")
            t2 = datetime.strptime(heure_fin.strip(), "%H:%M")
            temps_op = str(t2 - t1)

            new_data = {
                "Date": date,
                "Client": client,
                "N° Commande": commande,
                "Tissu": tissu,
                "Code Rouleau": code_rouleau,
                "Longueur Matelas": longueur,
                "Nombre de Plis": plis,
                "Heure Début": heure_debut,
                "Heure Fin": heure_fin,
                "Temps Opération": temps_op
            }

            save_entry(new_data)
            st.success(f"Données enregistrées avec succès. Temps opération : {temps_op}")
        except Exception as e:
            st.error(f"Erreur de format de l'heure : {e}")

# === Résumé ===
st.markdown("### Données enregistrées")
df = load_data()
st.dataframe(df)
