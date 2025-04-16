import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Fichier Excel ---
FILE_PATH = "donnee.xlsx"

# --- Initialiser fichier s'il n'existe pas ---
if not os.path.exists(FILE_PATH):
    df = pd.DataFrame(columns=[
        "Date", "Client", "Orders", "Fabric", "Roll Code",
        "Length", "Plies", "Start Time", "End Time", "Operation Time"
    ])
    df.to_excel(FILE_PATH, index=False)

# --- Titre ---
st.title("🧾 Interface de saisie de données")

# --- Champs du formulaire ---
with st.form("data_entry_form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.text_input("Date", value=datetime.now().strftime("%Y-%m-%d"))
        client = st.text_input("Client")
        orders = st.number_input("Orders", min_value=0)
        fabric = st.text_input("Fabric")
        roll_code = st.text_input("Roll Code")

    with col2:
        length = st.number_input("Length", min_value=0.0)
        plies = st.number_input("Plies", min_value=0)
        start_time = st.text_input("Start Time (HH:MM)")
        end_time = st.text_input("End Time (HH:MM)")

    submitted = st.form_submit_button("✅ Envoyer")

    if submitted:
        # --- Calcul de durée ---
        try:
            fmt = "%H:%M"
            start_dt = datetime.strptime(start_time, fmt)
            end_dt = datetime.strptime(end_time, fmt)
            if end_dt < start_dt:
                end_dt = end_dt.replace(day=start_dt.day + 1)
            duration = end_dt - start_dt
            hours, remainder = divmod(duration.seconds, 3600)
            minutes = remainder // 60
            op_time = f"{hours:02}:{minutes:02}"

            # --- Ajouter les données ---
            new_row = pd.DataFrame([[
                date, client, orders, fabric, roll_code,
                length, plies, start_time, end_time, op_time
            ]], columns=[
                "Date", "Client", "Orders", "Fabric", "Roll Code",
                "Length", "Plies", "Start Time", "End Time", "Operation Time"
            ])

            df = pd.read_excel(FILE_PATH)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(FILE_PATH, index=False)

            st.success("✅ Données enregistrées avec succès !")
            st.balloons()

        except Exception as e:
            st.error(f"⚠️ Erreur de format d'heure : {e}")
