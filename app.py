import streamlit as st
import pandas as pd
import os
from datetime import datetime
pip install streamlit pandas openpyxl


# --- Fichier Excel ---
FICHIER = "donnees.xlsx"

# --- Créer le fichier s'il n'existe pas ---
if not os.path.exists(FICHIER):
    df = pd.DataFrame(columns=[
        "Date", "Client", "Nombre de commandes", "Tissu", "Code rouleau",
        "Longueur de matelas", "Nombre de plis", "Heure de début", "Heure de fin", "Durée opération"
    ])
    df.to_excel(FICHIER, index=False)

# --- Titre ---
st.title("📋 Formulaire de Saisie de Données (Textile)")

# --- Formulaire ---
with st.form("formulaire_saisie"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.text_input("Date", value=datetime.now().strftime("%Y-%m-%d"))
        client = st.text_input("Client")
        commandes = st.number_input("Nombre de commandes", min_value=0)
        tissu = st.text_input("Tissu")
        code_rouleau = st.text_input("Code rouleau")

    with col2:
        longueur = st.number_input("Longueur de matelas (m)", min_value=0.0)
        plis = st.number_input("Nombre de plis", min_value=0)
        heure_debut = st.text_input("Heure de début (HH:MM)")
        heure_fin = st.text_input("Heure de fin (HH:MM)")

    envoyer = st.form_submit_button("✅ Enregistrer")

       if envoyer:
        try:
            # Calcul de la durée
            fmt = "%H:%M"
            h_debut = datetime.strptime(heure_debut, fmt)
            h_fin = datetime.strptime(heure_fin, fmt)
            if h_fin < h_debut:
                h_fin = h_fin.replace(day=h_debut.day + 1)
            duree = h_fin - h_debut
            heures, reste = divmod(duree.seconds, 3600)
            minutes = reste // 60
            duree_str = f"{heures:02}:{minutes:02}"

            nouvelle_ligne = pd.DataFrame([[
                date, client, commandes, tissu, code_rouleau,
                longueur, plis, heure_debut, heure_fin, duree_str
            ]], columns=[
                "Date", "Client", "Nombre de commandes", "Tissu", "Code rouleau",
                "Longueur de matelas", "Nombre de plis", "Heure de début", "Heure de fin", "Durée opération"
            ])

            # Lecture de l'existant
            try:
                df = pd.read_excel(FICHIER)
            except FileNotFoundError:
                df = pd.DataFrame(columns=nouvelle_ligne.columns)

            # Ajout et sauvegarde
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            df.to_excel(FICHIER, index=False)

            st.success(f"✅ Données enregistrées dans le fichier : {FICHIER}")
            st.balloons()

        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")
