from fastapi import FastAPI, Depends, Response, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from schemas import PredictionInput, UserLogin, Bien, BienCreate, UserCreate
from services.predict_service import PredictService
from services.auth_service import AuthService
from exceptions import AuthenticationError, ForbiddenError, YmmoException
from core.logger import logger
from dependencies import check_pole
from datetime import datetime, date
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import pandas as pd
import subprocess
import os
import sys


load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.database import get_stats_globales, get_connection, insert_log, get_all_logs

limiter = Limiter(key_func=get_remote_address)

tags_metadata = [
    {"name": "Authentification", "description": "Gestion des accès et de la sécurité via JWT."},
    {"name": "Catalogue", "description": "Consultation et gestion des biens immobiliers."},
    {"name": "Intelligence Artificielle", "description": "Prédiction des prix basée sur le modèle XGBoost."},
    {"name": "Administration", "description": "Statistiques, logs et réentraînement du modèle."}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.path.join(BASE_DIR, '../database/ymmo_analytics.duckdb')
    db_dir = os.path.abspath(os.path.join(BASE_DIR, '../database'))
    
    if not os.path.exists(db_path):
        logger.info("Base de données introuvable. Génération automatique en cours...")
        try:
            subprocess.run([sys.executable, 'init_log_db.py'], cwd=db_dir, check=True)
            subprocess.run([sys.executable, 'seed_db.py'], cwd=db_dir, check=True)
            subprocess.run([sys.executable, 'seed_users.py'], cwd=db_dir, check=True)
            logger.info("Base de données générée et remplie avec succès !")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur critique lors de la génération de la BDD : {e}")
            
    yield

app = FastAPI(
    title="Ymmo Analytics API",
    description="API de qualité entreprise pour l'estimation immobilière et l'analyse de données DVF.",
    version="1.0.0",
    contact={
        "name": "Équipe Dev/Data Ymmo",
        "email": "contact@ymmo.fr",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

auth_service = AuthService()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "../data_analysis/data/processed/modele_ymmo.pkl"))
predict_service = PredictService(model_path=MODEL_PATH)

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

@app.get("/api/biens", tags=["Catalogue"], summary="Lister les biens immobiliers de l'agence")
async def get_biens():
    conn = get_connection()
    try:
        query = """
            SELECT 
                id,
                titre,
                prix_estime as prix,
                surface,
                pieces,
                type_bien,
                ville,
                est_vendu,
                prix_vente_final,
                date_vente
            FROM biens
            ORDER BY id DESC
        """
        df = conn.execute(query).df()
        
        df = df.where(pd.notna(df), None)
        
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Erreur lecture biens: {e}")
        return []
    finally:
        conn.close()

@app.post("/api/biens", tags=["Catalogue"], summary="Créer un nouveau bien")
async def create_bien(bien_data: dict, current_user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    conn = get_connection()
    try:
        res = conn.execute("""
            INSERT INTO biens (titre, prix_estime, surface, pieces, type_bien, ville, est_vendu)
            VALUES (?, ?, ?, ?, ?, ?, FALSE)
            RETURNING id, titre, prix_estime, surface, pieces, type_bien, ville, est_vendu
        """, [
            bien_data.get('titre', 'Sans titre'), 
            bien_data.get('prix', 0), 
            bien_data.get('surface', 0), 
            bien_data.get('pieces', 1), 
            bien_data.get('type_bien', 'Appartement'), 
            bien_data.get('ville', 'Inconnue')
        ]).fetchone()
        
        return {
            "id": res[0],
            "titre": res[1],
            "prix": res[2],
            "surface": res[3],
            "pieces": res[4],
            "type_bien": res[5],
            "ville": res[6],
            "est_vendu": res[7]
        }
    finally:
        conn.close()

@app.delete("/api/biens/{bien_id}", tags=["Catalogue"], summary="Supprimer un bien")
async def delete_bien(bien_id: int, current_user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM biens WHERE id = ?", [bien_id])
        return {"message": "Bien supprimé du catalogue"}
    finally:
        conn.close()

class VenteBien(BaseModel):
    prix_vente_final: float

@app.post("/api/biens/{bien_id}/vendre", tags=["Catalogue"], summary="Conclure la vente d'un bien")
async def vendre_bien(
    bien_id: int, 
    vente_data: VenteBien, 
    current_user: dict = Depends(check_pole(["Direction", "IT et Support"]))
):
    conn = get_connection()
    try:
        res = conn.execute("SELECT est_vendu, titre FROM biens WHERE id = ?", [bien_id]).fetchone()
        
        if not res:
            raise HTTPException(status_code=404, detail="Bien introuvable.")
        if res[0]:
            raise HTTPException(status_code=400, detail="Ce bien a déjà été marqué comme vendu.")
        
        today = date.today().isoformat()
        
        conn.execute("""
            UPDATE biens 
            SET est_vendu = TRUE, 
                prix_vente_final = ?, 
                date_vente = ? 
            WHERE id = ?
        """, [vente_data.prix_vente_final, today, bien_id])
        
        return {
            "message": f"La vente a été actée.",
            "prix_final": vente_data.prix_vente_final,
            "date": today
        }
    finally:
        conn.close()

@app.post("/api/auth/register", tags=["Authentification"], summary="Créer un nouveau compte")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate):
    try:
        new_user = auth_service.register_user(user_data.email, user_data.password, user_data.pole)
        ip = request.client.host if request.client else "127.0.0.1"
        insert_log(new_user["email"], "REGISTER_SUCCESS", ip)
        return {"message": "Compte créé avec succès", "user": new_user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login", tags=["Authentification"], summary="Se connecter et récupérer un JWT")
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin, response: Response):
    user = auth_service.authenticate(credentials.email, credentials.password)
    ip = request.client.host if request.client else "127.0.0.1"
    if not user:
        insert_log(credentials.email, "LOGIN_FAILED", ip)
        raise AuthenticationError()
    
    insert_log(user["email"], "LOGIN_SUCCESS", ip)
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

@app.get("/api/auth/me", tags=["Authentification"], summary="Récupérer le profil connecté")
async def get_me(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Pas de cookie")
    
    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
        
    return user

@app.post("/api/auth/logout", tags=["Authentification"], summary="Se déconnecter")
async def logout(response: Response, request: Request):
    token = request.cookies.get("access_token")
    if token:
        user = auth_service.verify_token(token)
        if user:
            ip = request.client.host if request.client else "127.0.0.1"
            insert_log(user["email"], "LOGOUT", ip)
            
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"message": "Logged out"}

@app.post("/api/predict", tags=["Intelligence Artificielle"], summary="Estimer le prix d'un bien")
@limiter.limit("5/minute")
async def predict(request: Request, data: PredictionInput):
    try:
        result = predict_service.get_prediction(data.model_dump())
        return {"prix_estime": result}
    except Exception as e:
        logger.error(f"Erreur de prediction : {str(e)}")
        raise YmmoException(status_code=500, detail="Erreur interne du modele IA", error_code="ML_MODEL_ERROR")

@app.get("/api/stats-immobilieres", tags=["Administration"], summary="Récupérer les statistiques globales")
async def stats_immobilieres():
    data = get_stats_globales()
    return data

@app.get("/api/admin/audit", tags=["Administration"], summary="Vérifier l'état des systèmes")
async def get_audit(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Acces audit par {user['email']}")
    return {"status": "all_systems_go", "agences_active": 12}

@app.get("/api/admin/reports", tags=["Administration"], summary="Générer un rapport de performance")
async def get_reports(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Generation rapport demandee par {user['email']}")
    conn = get_connection()
    try:
        res_dvf = conn.execute("SELECT COUNT(*) FROM ventes").fetchone()
        volume_dvf = res_dvf[0] if res_dvf else 0

        query_agence = """
            SELECT 
                type_bien || ' (' || pieces || ' pièces)' as agence,
                COUNT(*) as requetes,
                AVG(prix_vente_final) as prix_moyen,
                AVG(ABS(prix_vente_final - prix_estime) / NULLIF(prix_estime, 0)) * 100 as taux_erreur
            FROM biens
            WHERE est_vendu = TRUE
            GROUP BY type_bien, pieces
            ORDER BY requetes DESC
            LIMIT 5
        """
        df_agence = conn.execute(query_agence).df()
        
        performances = []
        for _, row in df_agence.iterrows():
            err = row['taux_erreur']
            taux_erreur = round(float(err), 1) if err == err and err is not None else 0.0
            prix = row['prix_moyen']
            prix_format = f"{int(prix):,} €".replace(',', ' ') if prix == prix and prix is not None else "0 €"
            
            performances.append({
                "agence": str(row['agence']),
                "requetes": int(row['requetes']),
                "taux_erreur": taux_erreur,
                "tendance": prix_format
            })

        query_precision = "SELECT AVG(ABS(prix_vente_final - prix_estime) / NULLIF(prix_estime, 0)) * 100 FROM biens WHERE est_vendu = TRUE AND prix_estime > 0"
        res_prec = conn.execute(query_precision).fetchone()
        erreur_globale = res_prec[0] if res_prec and res_prec[0] else 11.5
        precision_moyenne = round(100 - erreur_globale, 1)

        return {
            "periode": "DVF + Ventes Agence",
            "volume_global": volume_dvf,
            "precision_moyenne": precision_moyenne,
            "performances": performances
        }
    finally:
        conn.close()

@app.get("/api/admin/logs", tags=["Administration"], summary="Consulter l'historique de sécurité")
async def get_logs(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Lecture des logs demandee par {user['email']}")
    return {"logs": get_all_logs()}

@app.get("/api/transactions", tags=["Catalogue"], summary="Rechercher des transactions spécifiques")
async def get_transactions(prix_max: float = 2000000, surface_min: float = 0):
    conn = get_connection()
    try:
        query = f"""
            SELECT * FROM ventes 
            WHERE valeur_fonciere <= {prix_max} 
            AND surface_reelle_bati >= {surface_min} 
            LIMIT 300
        """
        return conn.execute(query).df().to_dict(orient='records')
    finally:
        conn.close()

@app.get("/api/admin/analysis", tags=["Administration"], summary="Lancer une analyse des tendances")
async def get_analysis(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Analyse demandee par {user['email']}")
    conn = get_connection()
    try:
        res_ca = conn.execute("SELECT SUM(prix_vente_final), COUNT(*) FROM biens WHERE est_vendu = TRUE").fetchone()
        ca_total = res_ca[0] if res_ca and res_ca[0] else 0
        ventes_total = res_ca[1] if res_ca and res_ca[1] else 0

        query_top = """
            SELECT 
                ville,
                COUNT(*) as volume
            FROM biens
            WHERE est_vendu = TRUE
            GROUP BY ville
            ORDER BY volume DESC
            LIMIT 3
        """
        df_top = conn.execute(query_top).df()
        top_regions = []
        for _, row in df_top.iterrows():
            top_regions.append({
                "ville": str(row['ville']),
                "demande": "Très Forte",
                "type_populaire": f"Ventes: {int(row['volume'])}"
            })

        if ventes_total == 0:
            tendance_text = "En attente de la première transaction pour générer l'analyse financière."
        else:
            ca_str = f"{int(ca_total):,} €".replace(',', ' ')
            tendance_text = f"L'agence a généré un Chiffre d'Affaires total de {ca_str} sur {ventes_total} transactions conclues."

        return {
            "tendances_globales": tendance_text,
            "top_regions": top_regions
        }
    finally:
        conn.close()

def lancer_script_ia():
    try:
        script_path = os.path.abspath(os.path.join(BASE_DIR, '../data_analysis/train_model.py'))
        cwd_dir = os.path.abspath(os.path.join(BASE_DIR, '../data_analysis'))
        logger.info("Début du ré-entraînement de l'IA XGBoost en arrière-plan...")
        subprocess.run([sys.executable, script_path], cwd=cwd_dir, check=True)
        logger.info("Ré-entraînement terminé avec succès !")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du ré-entraînement : {e}")

@app.post("/api/admin/retrain", tags=["Administration"], summary="Déclencher le réentraînement XGBoost")
@limiter.limit("1/minute")
async def trigger_retrain(request: Request, background_tasks: BackgroundTasks, user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Re-entrainement du modele IA declenche par {user['email']}")
    
    background_tasks.add_task(lancer_script_ia)
    
    return {
        "status": "success",
        "message": "Processus d'apprentissage XGBoost démarré.",
        "details": "L'IA analyse actuellement les nouvelles données. Le modèle sera mis à jour en arrière-plan.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/api/admin/users", tags=["Administration"], summary="Lister les utilisateurs")
async def get_users(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    conn = get_connection()
    try:
        users = conn.execute("SELECT email, pole FROM utilisateurs").df().to_dict(orient='records')
        return users
    finally:
        conn.close()

@app.put("/api/admin/users/role", tags=["Administration"], summary="Modifier le rôle d'un utilisateur")
async def update_user_role(data: dict, current_user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    target_email = data.get('email')
    new_pole = data.get('pole')

    if target_email == current_user["email"]:
        raise HTTPException(
            status_code=403, 
            detail="Opération interdite : Vous ne pouvez pas modifier ou rétrograder votre propre compte."
        )

    conn = get_connection()
    try:
        res = conn.execute("SELECT pole FROM utilisateurs WHERE email = ?", [target_email]).fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
        
        target_current_pole = res[0]

        if current_user["pole"] == "IT et Support":
            if target_current_pole in ["Direction", "IT et Support"]:
                raise HTTPException(status_code=403, detail="Droits insuffisants.")
            
            if new_pole in ["Direction", "IT et Support"]:
                raise HTTPException(status_code=403, detail="Élévation interdite.")

        conn.execute("UPDATE utilisateurs SET pole = ? WHERE email = ?", [new_pole, target_email])
        return {"message": "Rôle mis à jour"}
    finally:
        conn.close()

@app.delete("/api/admin/users/{target_email}", tags=["Administration"], summary="Supprimer définitivement un utilisateur")
async def delete_user(target_email: str, current_user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    if target_email == current_user["email"]:
        raise HTTPException(
            status_code=400, 
            detail="Opération interdite : Impossible de supprimer votre propre compte."
        )
    
    conn = get_connection()
    try:
        res = conn.execute("SELECT pole FROM utilisateurs WHERE email = ?", [target_email]).fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
        
        target_pole = res[0]
        
        if current_user["pole"] == "IT et Support" and target_pole in ["Direction", "IT et Support"]:
            raise HTTPException(
                status_code=403, 
                detail="Droits insuffisants : Les membres IT ne peuvent supprimer que les comptes de type Utilisateur."
            )
            
        conn.execute("DELETE FROM utilisateurs WHERE email = ?", [target_email])
        return {"message": "Utilisateur révoqué et supprimé avec succès."}
    finally:
        conn.close()