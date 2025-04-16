import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.title("🧾 Interface de saisie de données - Coupage")

# 🖊️ Champs de formulaire
with st.form("saisie_form"):
    date = st.date_input("Date")
    client = st.text_input("Client")
    commande = st.text_input("N° commande")
    tissu = st.text_input("Tissu")
    code_rouleau = st.text_input("Code rouleau")
    longueur_matelas = st.number_input("Longueur matelas (en mètres)", min_value=0)
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

        # 🔗 Envoi vers Sheety
        sheety_endpoint = "https://api.sheety.co/2e31bbe32c21b55dd03dbf041b102e79/donnéesDeSuiviDeMatelassage/feuille1"

        new_row = {
            "feuille1": {
                "date": date.strftime("%Y-%m-%d"),
                "client": client,
                "numeroCommande": commande,
                "tissu": tissu,
                "codeRouleau": code_rouleau,
                "longueurMatelas": longueur_matelas,
                "nbPlis": nb_plis,
                "heureDebut": heure_debut.strftime("%H:%M"),
                "heureFin": heure_fin.strftime("%H:%M"),
                "tempsOperation": str(temps_operation)
            }
        }

        response = requests.post(sheety_endpoint, json=new_row)

        if response.status_code == 201:
            st.success("✅ Données enregistrées dans Google Sheets !")
        else:
            st.error(f"❌ Échec d'enregistrement : {response.text}")

    except Exception as e:
        st.error("❌ Une erreur est survenue : " + str(e))
