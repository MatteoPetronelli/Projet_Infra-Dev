from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
from schemas import BienImmobilier

app = FastAPI(title="API Ymmo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

modele = joblib.load("../data_analysis/data/processed/modele_ymmo.pkl")

@app.get("/api/status")
def read_root():
    return {"status": "API en ligne"}

@app.post("/api/predict")
def predict_price(bien: BienImmobilier):
    features = np.array([[
        bien.surface_reelle_bati, 
        bien.nombre_pieces_principales, 
        bien.longitude, 
        bien.latitude, 
        bien.est_maison
    ]])
    
    prediction = modele.predict(features)
    
    return {"prix_estime": round(prediction[0], 2)}