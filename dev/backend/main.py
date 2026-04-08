from fastapi import FastAPI, Depends, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import PredictionInput, UserLogin
from services.predict_service import PredictService
from services.auth_service import AuthService
from exceptions import AuthenticationError, ForbiddenError, YmmoException
from core.logger import logger
from dependencies import check_pole

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
        result = predict_service.get_prediction(data.dict())
        return {"prix_estime": result}
    except Exception as e:
        logger.error(f"Erreur de prediction : {str(e)}")
        raise YmmoException(status_code=500, detail="Erreur interne du modele IA", error_code="ML_MODEL_ERROR")

@app.get("/api/admin/audit")
async def get_audit(user: dict = Depends(check_pole(["Direction", "IT et Support"]))):
    logger.info(f"Acces audit par {user['email']}")
    return {"status": "all_systems_go", "agences_active": 12}