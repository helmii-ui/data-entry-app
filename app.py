import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, time, timedelta

# Fichiers
DATA_FILE = "donnees.xlsx"
CONFIG_FILE = "config.json"

# Matricule du chef de coupe
CHEF_MATRICULE = "chef123"  # Matricule du chef (à personnaliser)

# Liste initiale des clients
default_clients = ["HAVEP", "PWG", "Protec", "IS3", "MOERMAN", "TOYOTA", "Autre"]
if "clients" not in st.session_state:
    st.session_state.clients = default_clients.copy()

# Initialiser Excel avec des types de données appropriés si besoin
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

    if 'Date' in df.columns and not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'].dt.date == date_filter]

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
            file_name=f"donnees_filtrees_{date_filter}.csv",
            mime="text/csv"
        )
    elif export_option == "Excel":
        buffer = pd.io.excel.ExcelWriter(f"donnees_filtrees_{date_filter}.xlsx")
        df.to_excel(buffer, index=False)
        buffer.close()
        
        with open(f"donnees_filtrees_{date_filter}.xlsx", "rb") as f:
            st.download_button(
                label="Télécharger en Excel",
                data=f,
                file_name=f"donnees_filtrees_{date_filter}.xlsx",
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
        
        # Calcul automatique de la durée en minutes
        def calculate_duration(start, end):
            # Convertir en datetime pour faciliter le calcul
            start_dt = datetime.combine(datetime.today(), start)
            end_dt = datetime.combine(datetime.today(), end)
            
            # Si fin est avant début, on suppose que c'est le jour suivant
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
                
            # Calculer la différence en minutes
            duration = (end_dt - start_dt).total_seconds() / 60
            return round(duration)
        
        duree_minutes = calculate_duration(debut, fin)
        
        st.info(f"Durée calculée: {duree_minutes} minutes")
        
        operateur = st.text_input("Nom Opérateur", value=default_operator.get("nom", ""))
        matricule = input_matricule

        submitted = st.form_submit_button("Valider")
        if submitted:
            if not client:
                st.error("Veuillez entrer un nom de client valide.")
            else:
                # Ajouter ligne avec des noms de colonnes sans espaces et caractères spéciaux
                new_row = pd.DataFrame([[
                    date, client, commande, tissu, rouleau, longueur, plis, 
                    debut, fin, duree_minutes, operateur, matricule
                ]], columns=[
                    "Date", "Client", "N_Commande", "Tissu", "Code_Rouleau", 
                    "Longueur_Matelas", "Nombre_Plis", "Heure_Debut", 
                    "Heure_Fin", "Duree_Minutes", "Nom_Operateur", "Matricule"
                ])
                
                # Charger les données existantes
                if os.path.exists(DATA_FILE):
                    df = pd.read_excel(DATA_FILE)
                    
                    # Vérifier/ajuster les noms de colonnes pour compatibilité
                    df.columns = [col.replace(" ", "_").replace("°", "") for col in df.columns]
                    
                    # Concaténer
                    df = pd.concat([df, new_row], ignore_index=True)
                else:
                    df = new_row
                    
                # Enregistrer
                df.to_excel(DATA_FILE, index=False)

                # Mettre à jour config
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"nom": operateur, "matricule": matricule}, f)

                st.success("✅ Données enregistrées avec succès !")

    # 🗂️ Affichage tableau
    st.subheader("Données enregistrées aujourd'hui")
    df = pd.read_excel(DATA_FILE)
    
    # Filtrer pour n'afficher que les données d'aujourd'hui
    if 'Date' in df.columns and not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        today_data = df[df['Date'].dt.date == datetime.today().date()]
        st.dataframe(today_data)
    else:
        st.dataframe(df)

    # Ajouter des statistiques simples
    if not df.empty:
        st.subheader("Statistiques")
        total_matelas = len(df)
        total_metrage = df['Longueur_Matelas'].sum() if 'Longueur_Matelas' in df.columns else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Matelas", total_matelas)
        with col2:
            st.metric("Total Métrage (m)", f"{total_metrage:.2f}")

else:
    if input_matricule:
        st.error("Matricule incorrect. Accès refusé.")
