import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, time, timedelta

# Fichiers
DATA_FILE = "donnees.xlsx"
CONFIG_FILE = "config.json"

# Matricule du chef de coupe
CHEF_MATRICULE = "chef123"

# Liste initiale des clients
default_clients = ["HAVEP", "PWG", "Protec", "IS3", "MOERMAN", "TOYOTA", "Autre"]
if "clients" not in st.session_state:
    st.session_state.clients = default_clients.copy()

# Initialiser Excel
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Date", "Client", "N_Commande", "Tissu", "Code_Rouleau",
        "Longueur_Matelas", "Nombre_Plis", "Heure_Debut",
        "Heure_Fin", "Duree_Minutes", "Nom_Operateur", "Matricule"
    ])
    df_init.to_excel(DATA_FILE, index=False)

# Charger config opérateur
default_operator = {"nom": "", "matricule": ""}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        default_operator = json.load(f)

# Titre
st.title("Interface - Atelier de Coupe")

# Authentification
input_matricule = st.text_input("Entrer votre matricule", type="password")

# Accès Chef
if input_matricule == CHEF_MATRICULE:
    st.success("Bienvenue Chef (accès lecture seule)")

    st.subheader("Filtrer les données")
    client_filter = st.selectbox("Filtrer par client", options=["Tous"] + st.session_state.clients)
    date_filter = st.date_input("Filtrer par date", value=datetime.today(), max_value=datetime.today())

    df = pd.read_excel(DATA_FILE)

    if client_filter != "Tous":
        df = df[df['Client'] == client_filter]

    if 'Date' in df.columns and not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'].dt.date == date_filter]

    st.subheader("Données enregistrées")
    st.dataframe(df)

    st.subheader("Exporter les données")
    export_option = st.selectbox("Exporter en format", options=["Sélectionner", "CSV", "Excel"])

    if export_option == "CSV":
        st.download_button(
            label="Télécharger en CSV",
            data=df.to_csv(index=False),
            file_name=f"donnees_filtrees_{date_filter}.csv",
            mime="text/csv"
        )
    elif export_option == "Excel":
        df.to_excel("donnees_temp_export.xlsx", index=False)
        with open("donnees_temp_export.xlsx", "rb") as f:
            st.download_button(
                label="Télécharger en Excel",
                data=f,
                file_name=f"donnees_filtrees_{date_filter}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Accès Opérateur
elif input_matricule == default_operator.get("matricule"):
    st.success("Accès opérateur autorisé.")

    # Initialiser session_state pour chaque champ
    default_values = {
        "client": st.session_state.clients[0],
        "commande": "",
        "tissu": "",
        "rouleau": "",
        "longueur": 0.0,
        "plis": 1,
        "debut": time(8, 0),
        "fin": time(9, 0),
        "operateur": default_operator.get("nom", "")
    }

    for key, val in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Réinitialiser le formulaire
    if st.button("Réinitialiser le formulaire"):
        for key, val in default_values.items():
            st.session_state[key] = val
        st.rerun()

    with st.form("form_saisie"):
        date = st.date_input("Date", value=datetime.now())
        client_selection = st.selectbox("Client", options=st.session_state.clients, key="client")

        if client_selection == "Autre":
            nouveau_client = st.text_input("Nom du nouveau client")
            if nouveau_client:
                client = nouveau_client
                if nouveau_client not in st.session_state.clients:
                    st.session_state.clients.insert(-1, nouveau_client)
                    st.success(f"Client ajouté : {nouveau_client}")
            else:
                client = ""
        else:
            client = client_selection

        commande = st.text_input("N° Commande", key="commande")
        tissu = st.text_input("Tissu", key="tissu")
        rouleau = st.text_input("Code Rouleau", key="rouleau")
        longueur = st.number_input("Longueur Matelas (m)", min_value=0.0, step=0.1, key="longueur")
        plis = st.number_input("Nombre de Plis", min_value=1, step=1, key="plis")
        debut = st.time_input("Heure Début", key="debut")
        fin = st.time_input("Heure Fin", key="fin")

        def calculate_duration(start, end):
            start_dt = datetime.combine(datetime.today(), start)
            end_dt = datetime.combine(datetime.today(), end)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            return round((end_dt - start_dt).total_seconds() / 60)

        duree_minutes = calculate_duration(debut, fin)
        st.info(f"Durée calculée: {duree_minutes} minutes")

        operateur = st.text_input("Nom Opérateur", key="operateur")
        matricule = input_matricule

        submitted = st.form_submit_button("Valider")
        if submitted:
            if not client:
                st.error("Veuillez entrer un nom de client valide.")
            else:
                new_row = pd.DataFrame([[date, client, commande, tissu, rouleau, longueur, plis,
                                         debut, fin, duree_minutes, operateur, matricule]],
                                       columns=["Date", "Client", "N_Commande", "Tissu", "Code_Rouleau",
                                                "Longueur_Matelas", "Nombre_Plis", "Heure_Debut",
                                                "Heure_Fin", "Duree_Minutes", "Nom_Operateur", "Matricule"])

                if os.path.exists(DATA_FILE):
                    df = pd.read_excel(DATA_FILE)
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df = new_row

                df.to_excel(DATA_FILE, index=False)

                with open(CONFIG_FILE, "w") as f:
                    json.dump({"nom": operateur, "matricule": matricule}, f)

                st.success("✅ Données enregistrées avec succès !")

    st.subheader("Données enregistrées aujourd'hui")
    df = pd.read_excel(DATA_FILE)
    if 'Date' in df.columns and not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        today_data = df[df['Date'].dt.date == datetime.today().date()]
        st.dataframe(today_data)
    else:
        st.dataframe(df)

    if not df.empty:
        st.subheader("Statistiques")
        total_matelas = len(df)
        total_metrage = df['Longueur_Matelas'].sum() if 'Longueur_Matelas' in df.columns else 0

        col1, col2 = st.columns(2)
        col1.metric("Total Matelas", total_matelas)
        col2.metric("Total Métrage (m)", f"{total_metrage:.2f}")

else:
    if input_matricule:
        st.error("Matricule incorrect. Accès refusé.")
