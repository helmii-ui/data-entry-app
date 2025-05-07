import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Chemins des fichiers
DATA_FILE = "donnees.xlsx"
CONFIG_FILE = "config.json"

# Initialiser Excel si inexistant
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Date", "Client", "N° Commande", "Tissu", "Code Rouleau", 
        "Longueur Matelas", "Nombre de Plis", "Heure Début", 
        "Heure Fin", "Temps Matelas", "Nom Opérateur", "Matricule"
    ])
    df_init.to_excel(DATA_FILE, index=False)

# Lire config (nom + matricule autorisé)
default_operator = {"nom": "", "matricule": ""}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        default_operator = json.load(f)

st.title("Interface de Saisie - Atelier de Coupe")

# 🔒 Authentification par matricule
input_matricule = st.text_input("Entrer votre matricule pour accéder au formulaire", type="password")

if input_matricule == default_operator.get("matricule"):
    st.success("Accès autorisé.")
    
    with st.form("form_saisie"):
        date = st.date_input("Date", value=datetime.now())
        client = st.text_input("Client")
        commande = st.text_input("N° Commande")
        tissu = st.text_input("Tissu")
        rouleau = st.text_input("Code Rouleau")
        longueur = st.number_input("Longueur Matelas (m)", min_value=0.0, step=0.1)
        plis = st.number_input("Nombre de Plis", min_value=1, step=1)
        debut = st.time_input("Heure Début")
        fin = st.time_input("Heure Fin")
        temps = st.text_input("Temps de Matelas (hh:mm)")

        # Préremplir nom + matricule
        operateur = st.text_input("Nom Opérateur", value=default_operator.get("nom", ""))
        matricule = input_matricule  # sécurisé

        submitted = st.form_submit_button("Valider")
        if submitted:
            # Enregistrement
            new_row = pd.DataFrame([[
                date, client, commande, tissu, rouleau, longueur, plis, 
                debut, fin, temps, operateur, matricule
            ]], columns=[
                "Date", "Client", "N° Commande", "Tissu", "Code Rouleau", 
                "Longueur Matelas", "Nombre de Plis", "Heure Début", 
                "Heure Fin", "Temps Matelas", "Nom Opérateur", "Matricule"
            ])
            df = pd.read_excel(DATA_FILE)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(DATA_FILE, index=False)

            # Mise à jour config
            with open(CONFIG_FILE, "w") as f:
                json.dump({"nom": operateur, "matricule": matricule}, f)

            st.success("Données enregistrées avec succès !")

else:
    if input_matricule:
        st.error("Matricule incorrect. Accès refusé.")
