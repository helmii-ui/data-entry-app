import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Saisie de données", layout="centered")
st.title("📄 Interface de saisie de données (Excel local)")

FILENAME = "data.xlsx"

# 1. Charger ou créer le fichier Excel
if os.path.exists(FILENAME):
    df = pd.read_excel(FILENAME)
else:
    df = pd.DataFrame(columns=[
        "Date", "Client", "N° Commande", "Tissu", "Code Rouleau", 
        "Longueur Matelas", "Nombre de Plis", "Heure Début", "Heure Fin", 
        "Temps Opération", "Matricule", "Nom Opérateur"
    ])
    df.to_excel(FILENAME, index=False)

# 2. Afficher les données existantes
st.subheader("Données existantes")
st.dataframe(df, use_container_width=True)

# 3. Formulaire de saisie
st.subheader("📝 Formulaire de saisie")

with st.form("formulaire_saisie"):
    date = st.date_input("Date", value=datetime.today())
    client = st.selectbox("Client", ["Decathlon", "Benetton", "Zara", "Autre"])
    num_commande = st.text_input("N° Commande")
    tissu = st.text_input("Tissu")
    code_rouleau = st.text_input("Code Rouleau")
    longueur_matelas = st.number_input("Longueur Matelas (m)", min_value=0.0, step=0.1)
    nb_plis = st.number_input("Nombre de Plis", min_value=1, step=1)
    heure_debut = st.time_input("Heure Début")
    heure_fin = st.time_input("Heure Fin")
    temps_operation = st.text_input("Temps de l'opération")
    matricule = st.text_input("Matricule opérateur")
    nom_operateur = st.text_input("Nom opérateur")

    submitted = st.form_submit_button("Enregistrer")

    if submitted:
        if not matricule or not nom_operateur:
            st.warning("❗ Matricule et nom de l'opérateur sont obligatoires.")
        else:
            new_row = {
                "Date": date,
                "Client": client,
                "N° Commande": num_commande,
                "Tissu": tissu,
                "Code Rouleau": code_rouleau,
                "Longueur Matelas": longueur_matelas,
                "Nombre de Plis": nb_plis,
                "Heure Début": heure_debut.strftime("%H:%M"),
                "Heure Fin": heure_fin.strftime("%H:%M"),
                "Temps Opération": temps_operation,
                "Matricule": matricule,
                "Nom Opérateur": nom_operateur
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(FILENAME, index=False)
            st.success("✅ Données enregistrées avec succès !")


# Fichiers
DATA_FILE = "donnees.xlsx"
CONFIG_FILE = "config.json"

# Matricule du chef de coupe
CHEF_MATRICULE = "chef123"  # Matricule du chef (à personnaliser)

# Liste initiale des clients
default_clients = ["HAVEP", "PWG", "Protec", "IS3","MOERMAN","TOYOTA", "Autre"]
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

# Titre de l'interface
st.title("Interface - Atelier de Coupe")

# Authentification
input_matricule = st.text_input("Entrer votre matricule", type="password")

# Accès chef de coupe
if input_matricule == CHEF_MATRICULE:
    st.success("Bienvenue Chef (accès lecture seule)")

    # Filtrage des données
    st.subheader("Filtrer les données")
    client_filter = st.selectbox("Filtrer par client", options=["Tous"] + st.session_state.clients)
    date_filter = st.date_input("Filtrer par date", value=datetime.today(), max_value=datetime.today())

    # Lire les données
    df = pd.read_excel(DATA_FILE)

    # Filtrer les données en fonction des choix
    if client_filter != "Tous":
        df = df[df['Client'] == client_filter]

    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'] == pd.to_datetime(date_filter)]

    # Afficher les données filtrées
    st.subheader("Données enregistrées")
    st.dataframe(df)

    # Option d'exportation
    st.subheader("Exporter les données")
    export_option = st.selectbox("Exporter en format", options=["Sélectionner", "CSV", "Excel"])
    
    if export_option == "CSV":
        st.download_button(
            label="Télécharger en CSV",
            data=df.to_csv(index=False),
            file_name="donnees_filtrees.csv",
            mime="text/csv"
        )
    elif export_option == "Excel":
        st.download_button(
            label="Télécharger en Excel",
            data=df.to_excel(index=False),
            file_name="donnees_filtrees.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif input_matricule == default_operator.get("matricule"):
    st.success("Accès opérateur autorisé.")

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
