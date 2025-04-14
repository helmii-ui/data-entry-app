import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("🧾 Interface de saisie de données - Coupage")

# 🖊️ Champs de formulaire
with st.form("saisie_form"):
    date = st.date_input("Date")
    client = st.text_input("Client")
    commande = st.text_input("N° commande")
    tissu = st.text_input("Tissu")
    code_rouleau = st.text_input("Code rouleau")
    longueur = st.number_input("Longueur matelas (en mètres)", min_value=0)
    nb_plis = st.number_input("Nombre de plis", min_value=0)
    heure_debut = st.time_input("Heure de début")
    heure_fin = st.time_input("Heure de fin")
    
    submitted = st.form_submit_button("📥 Enregistrer")

if submitted:
    try:
        # 🧮 Calcul du temps d'opération
        fmt = "%H:%M:%S"
        t1 = datetime.strptime(str(heure_debut), fmt)
        t2 = datetime.strptime(str(heure_fin), fmt)
        temps_operation = int((t2 - t1).total_seconds() / 60)
        
        new_data = {
            "Date": [date],
            "Client": [client],
            "N° commande": [commande],
            "Tissu": [tissu],
            "Code rouleau": [code_rouleau],
            "Longueur matelas": [longueur],
            "Nb plis": [nb_plis],
            "Heure début": [heure_debut],
            "Heure fin": [heure_fin],
            "Temps opération (min)": [temps_operation]
        }

        df = pd.DataFrame(new_data)

        file_path = "donnees_saisies.xlsx"
        
        # Si fichier existe, on ajoute les nouvelles données
        if os.path.exists(file_path):
            old_df = pd.read_excel(file_path)
            df = pd.concat([old_df, df], ignore_index=True)
        
        df.to_excel(file_path, index=False)
        st.success(f"✅ Données enregistrées avec succès ! Temps opération : {temps_operation} min")
        st.download_button("⬇️ Télécharger le fichier Excel", data=open(file_path, "rb"), file_name="donnees_saisies.xlsx")

    except Exception as e:
        st.error("❌ Une erreur est survenue : " + str(e))
