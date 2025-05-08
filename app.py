import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import threading
import time

# Fichier de données
DATA_FILE = "donnees.xlsx"

# Modèles de données
class EnregistrementBase(BaseModel):
    Client: str
    N_Commande: str
    Tissu: str
    Code_Rouleau: str
    Longueur_Matelas: float
    Nombre_Plis: int
    Heure_Debut: str
    Heure_Fin: str
    Duree_Minutes: int
    Nom_Operateur: str
    Matricule: str

class Enregistrement(EnregistrementBase):
    Date: str

# Créer l'application FastAPI
api = FastAPI(title="API Atelier de Coupe", 
              description="API pour l'intégration entre Streamlit et Power BI",
              version="1.0.0")

# Activer CORS pour permettre les requêtes depuis Power BI
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vérifier si le fichier Excel existe
def get_dataframe():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE)
    else:
        # Créer un DataFrame vide avec les bonnes colonnes
        return pd.DataFrame(columns=[
            "Date", "Client", "N_Commande", "Tissu", "Code_Rouleau", 
            "Longueur_Matelas", "Nombre_Plis", "Heure_Debut", 
            "Heure_Fin", "Duree_Minutes", "Nom_Operateur", "Matricule"
        ])

# Routes API
@api.get("/")
def read_root():
    return {"message": "API Atelier de Coupe", "status": "En ligne"}

@api.get("/donnees", response_model=List[dict])
def get_donnees():
    df = get_dataframe()
    # Convertir les dates en chaînes pour la sérialisation JSON
    if 'Date' in df.columns and not df.empty:
        df['Date'] = df['Date'].astype(str)
    return df.to_dict('records')

@api.get("/donnees/client/{client}")
def get_donnees_par_client(client: str):
    df = get_dataframe()
    filtered_df = df[df['Client'] == client]
    if 'Date' in filtered_df.columns and not filtered_df.empty:
        filtered_df['Date'] = filtered_df['Date'].astype(str)
    return filtered_df.to_dict('records')

@api.get("/donnees/date/{date}")
def get_donnees_par_date(date: str):
    df = get_dataframe()
    if 'Date' in df.columns and not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date.astype(str)
        filtered_df = df[df['Date'] == date]
        return filtered_df.to_dict('records')
    return []

@api.post("/donnees/ajouter")
def ajouter_donnee(enregistrement: Enregistrement):
    try:
        df = get_dataframe()
        
        # Convertir l'objet Pydantic en dictionnaire
        new_data = enregistrement.dict()
        
        # Ajouter à DataFrame
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        
        # Sauvegarder
        df.to_excel(DATA_FILE, index=False)
        
        return {"status": "success", "message": "Donnée ajoutée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/statistiques")
def get_statistiques():
    df = get_dataframe()
    if df.empty:
        return {"total_matelas": 0, "total_metrage": 0, "temps_total_minutes": 0}
    
    total_matelas = len(df)
    total_metrage = df['Longueur_Matelas'].sum() if 'Longueur_Matelas' in df.columns else 0
    temps_total = df['Duree_Minutes'].sum() if 'Duree_Minutes' in df.columns else 0
    
    return {
        "total_matelas": total_matelas,
        "total_metrage": float(total_metrage),
        "temps_total_minutes": int(temps_total)
    }

# Fonction pour démarrer l'API dans un thread séparé
def start_api():
    uvicorn.run(api, host="0.0.0.0", port=8000)

# Fonction pour exécuter dans Streamlit
def main():
    st.title("API Atelier de Coupe")
    st.info("Cette application expose vos données via une API REST pour Power BI")
    
    if st.button("Démarrer l'API"):
        api_thread = threading.Thread(target=start_api)
        api_thread.daemon = True
        api_thread.start()
        st.success("✅ API démarrée sur http://localhost:8000")
        st.info("Utilisez cette URL dans Power BI pour vous connecter à vos données")
        
        # Guide d'utilisation
        st.subheader("Endpoints disponibles:")
        st.code("""
        GET /donnees - Toutes les données
        GET /donnees/client/{client} - Données filtrées par client
        GET /donnees/date/{date} - Données filtrées par date (format YYYY-MM-DD)
        GET /statistiques - Statistiques globales
        POST /donnees/ajouter - Ajouter une nouvelle entrée
        """)
        
        # Afficher l'état en attente
        with st.spinner("API en cours d'exécution... Ne fermez pas cette fenêtre"):
            while True:
                time.sleep(1)
                
    st.warning("⚠️ Important: Gardez cette fenêtre ouverte pour que l'API continue à fonctionner")
    
if __name__ == "__main__":
    main()
