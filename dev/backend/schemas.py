from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class PredictionInput(BaseModel):
    surface_reelle_bati: float = Field(..., gt=0, lt=10001)
    nombre_pieces_principales: int = Field(..., gt=0, lt=501)
    longitude: float
    latitude: float
    est_maison: int = Field(..., ge=0, le=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Bien(BaseModel):
    id: int
    titre: str
    prix: float
    surface: float
    pieces: int
    type_bien: str  # "Maison" ou "Appartement"
    est_vendu: bool = False
    ville: str

class BienCreate(BaseModel):
    titre: str
    prix: float
    surface: float
    pieces: int
    type_bien: str
    ville: str