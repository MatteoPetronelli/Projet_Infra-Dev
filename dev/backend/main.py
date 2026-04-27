from fastapi import FastAPI, Depends, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import PredictionInput, UserLogin, Bien, BienCreate
from services.predict_service import PredictService
from services.auth_service import AuthService
from exceptions import AuthenticationError, ForbiddenError, YmmoException
from core.logger import logger
from dependencies import check_pole
from datetime import datetime
from typing import List
import polars as pl
import os

app = FastAPI(title="Ymmo Analytics API")

auth_service = AuthService()
predict_service = PredictService(model_path="../data_analysis/data/processed/modele_ymmo.pkl")

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_BIENS = [
    {"id": 1, "titre": "Superbe T3 centre-ville", "prix": 250000, "surface": 65, "pieces": 3, "type_bien": "Appartement", "est_vendu": False, "ville": "Aix-en-Provence"},
    {"id": 2, "titre": "Maison familiale avec jardin", "prix": 450000, "surface": 120, "pieces": 5, "type_bien": "Maison", "est_vendu": False, "ville": "Lyon"},
    {"id": 3, "titre": "Studio etudiant proche fac", "prix": 110000, "surface": 25, "pieces": 1, "type_bien": "Appartement", "est_vendu": True, "ville": "Marseille"}
]
compteur_id = 4

@app.get("/api/biens", response_model=List[Bien])
async def get_biens():
    return MOCK_BIENS

@app.post("/api/biens", response_model=Bien)
async def create_bien(bien: BienCreate):
    global compteur_id
    nouveau_bien = bien.model_dump()
    nouveau_bien["id"] = compteur_id
    nouveau_bien["est_vendu"] = False
    MOCK_BIENS.append(nouveau_bien)
    compteur_id += 1
    return nouveau_bien

@app.delete("/api/biens/{bien_id}")
async def delete_bien(bien_id: int):
    global MOCK_BIENS
    MOCK_BIENS = [b for b in MOCK_BIENS if b["id"] != bien_id]
    return {"message": "Bien supprime"}

@app.post("/api/auth/login")
async def login(credentials: UserLogin, response: Response):
    user = auth_service.authenticate(credentials.email, credentials.password)
    if not user:
        raise AuthenticationError()
    
    token = auth_service.create_access_token({"email": user["email"], "pole": user["pole"]})
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax",
        secure=False,
        path="/"
    )
    
    return user

@app.get("/api/auth/me")
async def get_me(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Pas de cookie")
    
    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
        
    return user

@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"message": "Logged out"}

@app.post("/api/predict")
async def predict(data: PredictionInput):
    try:
        result = predict_service.get_prediction(data.model_dump())
        return {"prix_estime": result}
    except Exception as e:
        logger.error(f"Erreur de prediction : {str(e)}")
        raise YmmoException(status_code=500, detail="Erreur interne du modele IA", error_code="ML_MODEL_ERROR")

@app.get("/api/admin/audit")
async def get_audit(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Acces audit par {user['email']}")
    return {"status": "all_systems_go", "agences_active": 12}

@app.get("/api/admin/reports")
async def get_reports(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Generation rapport demandee par {user['email']}")
    return {
        "periode": "Avril 2026",
        "volume_global": 1450,
        "precision_moyenne": 88.5,
        "performances": [
            {"agence": "Aix-en-Provence", "requetes": 507, "taux_erreur": 5.2, "tendance": "+12%"},
            {"agence": "Lyon Presqu'ile", "requetes": 412, "taux_erreur": 6.1, "tendance": "+5%"},
            {"agence": "Paris 15", "requetes": 342, "taux_erreur": 7.4, "tendance": "-2%"},
            {"agence": "Marseille Prado", "requetes": 189, "taux_erreur": 8.9, "tendance": "+1%"}
        ]
    }

@app.get("/api/admin/logs")
async def get_logs(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Lecture des logs demandee par {user['email']}")
    return {
        "logs": [
            {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user": user["email"], "action": "LOGIN_SUCCESS", "ip": "127.0.0.1"},
            {"timestamp": "2026-04-10 09:12:05", "user": "inconnu", "action": "LOGIN_FAILED", "ip": "192.168.1.45"},
            {"timestamp": "2026-04-10 08:30:00", "user": "agent.aix@ymmo.fr", "action": "LOGOUT", "ip": "10.0.0.14"},
            {"timestamp": "2026-04-09 18:15:33", "user": "agent.lyon@ymmo.fr", "action": "LOGIN_SUCCESS", "ip": "10.0.0.22"},
            {"timestamp": "2026-04-09 18:14:00", "user": "agent.lyon@ymmo.fr", "action": "LOGIN_FAILED", "ip": "10.0.0.22"}
        ]
    }

try:
    csv_path = "../data_analysis/data/processed/dvf_clean.csv"
    if os.path.exists(csv_path):
        df_dvf = pl.read_csv(csv_path)
        df_sample = df_dvf.sample(n=2000, seed=42)
        DVF_DATA = df_sample.to_dicts()
        logger.info("Donnees DVF chargees en memoire.")
    else:
        DVF_DATA = []
except Exception as e:
    logger.error(f"Erreur chargement DVF: {e}")
    DVF_DATA = []

@app.get("/api/transactions")
async def get_transactions(prix_max: float = 2000000, surface_min: float = 0):
    filtered = [
        t for t in DVF_DATA
        if t["valeur_fonciere"] <= prix_max and t["surface_reelle_bati"] >= surface_min
    ]
    return filtered[:300]

@app.get("/api/admin/analysis")
async def get_analysis(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Analyse des biens populaires demandee par {user['email']}")
    return {
        "tendances_globales": "Augmentation de 15% des recherches pour des biens avec exterieur depuis 3 mois.",
        "top_regions": [
            {"ville": "Aix-en-Provence", "demande": "Forte", "type_populaire": "Appartement T3"},
            {"ville": "Lyon Presqu'ile", "demande": "Tres Forte", "type_populaire": "Appartement T2"},
            {"ville": "Marseille Prado", "demande": "Moyenne", "type_populaire": "Maison avec jardin"}
        ]
    }

@app.post("/api/admin/retrain")
async def trigger_retrain(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Re-entrainement du modele IA declenche par {user['email']}")
    return {
        "status": "success",
        "message": "Processus d'apprentissage XGBoost demarre.",
        "details": "Integration des nouvelles donnees DVF en cours. Duree estimee : 4 minutes.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }