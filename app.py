import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Fichiers
DATA_FILE = "donnees.xlsx"
CONFIG_FILE = "config.json"

# Liste initiale des clients
default_clients = ["HAVEP", "PWG", "Samsonite", "IS3", "MOERMAN","TOYOTA","Autre"]
if "clients" not in st.session_state:
    st.session_state.clients = default_clients.copy()

# Initialiser Excel si besoin
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Date", "Client", "N° Commande", "Tissu", "Code Rouleau", 
        "Longueur Matelas", "Nombre de Plis", "Heure Début", 
        "Heure Fin", "Temps Matelas", "Nom Opérateur", "Matricule"
    ])
    df_init.to_excel(DATA_FILE, index=False)

# Charger config opérateur
default_operator = {"nom": "", "matricule": ""}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        default_operator = json.load(f)

st.title("Interface de Saisie - Atelier de Coupe")

# 🔒 Accès avec matricule
input_matricule = st.text_input("Entrer votre matricule pour accéder au formulaire", type="password")

if input_matricule == default_operator.get("matricule"):
    st.success("Accès autorisé.")

    with st.form("form_saisie"):
        date = st.date_input("Date", value=datetime.now())

        # Liste déroulante client
        client_selection = st.selectbox("Client", options=st.session_state.clients)

        # Si "Autre", proposer un champ pour ajouter
        if client_selection == "Autre":
            nouveau_client = st.text_input("Nom du nouveau client")
            if nouveau_client:
                client = nouveau_client
                if nouveau_client not in st.session_state.clients:
                    st.session_state.clients.insert(-1, nouveau_client)
                    st.success(f"Client ajouté à la liste : {nouveau_client}")
            else:
                client = ""
        else:
            client = client_selection

        commande = st.text_input("N° Commande")
        tissu = st.text_input("Tissu")
        rouleau = st.text_input("Code Rouleau")
        longueur = st.number_input("Longueur Matelas (m)", min_value=0.0, step=0.1)
        plis = st.number_input("Nombre de Plis", min_value=1, step=1)
        debut = st.time_input("Heure Début")
        fin = st.time_input("Heure Fin")
        temps = st.text_input("Temps de Matelas (hh:mm)")

        operateur = st.text_input("Nom Opérateur", value=default_operator.get("nom", ""))
        matricule = input_matricule

        submitted = st.form_submit_button("Valider")
        if submitted:
            if not client:
                st.error("Veuillez entrer un nom de client valide.")
            else:
                # Ajouter ligne
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

                # Mettre à jour config
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"nom": operateur, "matricule": matricule}, f)

                st.success("✅ Données enregistrées avec succès !")

    # 🗂️ Affichage tableau
    st.subheader("Données enregistrées")
    df = pd.read_excel(DATA_FILE)
    st.dataframe(df)

else:
    if input_matricule:
        st.error("Matricule incorrect. Accès refusé.")
