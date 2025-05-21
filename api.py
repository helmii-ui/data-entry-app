from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import pandas as pd
import os

app = FastAPI(title="Atelier de Coupe API")

# Configuration de sécurité (clé API simple)
API_KEY = "votre_cle_secrete"  # Changez ceci pour une clé sécurisée
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Chemin vers le fichier de données
DATA_FILE = "donnees.xlsx"

# Vérification de la clé API
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Clé API invalide"
        )
    return api_key

@app.get("/donnees", dependencies=[Depends(get_api_key)])
async def get_donnees():
    """Récupérer toutes les données au format JSON"""
    if not os.path.exists(DATA_FILE):
        return {"error": "Fichier de données non trouvé"}
    
    try:
        df = pd.read_excel(DATA_FILE)
        # Convertir les dates en format ISO pour JSON
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Convertir les heures en chaînes pour JSON
        for col in ['Heure Début', 'Heure Fin']:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

# Lancer l'API avec uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
