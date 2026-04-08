from pydantic import BaseModel, Field, EmailStr

class PredictionInput(BaseModel):
    surface_reelle_bati: float = Field(..., gt=0, lt=10001)
    nombre_pieces_principales: int = Field(..., gt=0, lt=501)
    longitude: float
    latitude: float
    est_maison: int = Field(..., ge=0, le=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str