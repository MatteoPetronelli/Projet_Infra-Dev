from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class PredictionInput(BaseModel):
    surface_reelle_bati: float = Field(..., gt=0, lt=10001, description="Surface en mètres carrés")
    nombre_pieces_principales: int = Field(..., gt=0, lt=501, description="Nombre de pièces")
    longitude: float = Field(..., description="Coordonnées de longitude")
    latitude: float = Field(..., description="Coordonnées de latitude")
    est_maison: int = Field(..., ge=0, le=1, description="1 pour Maison, 0 pour Appartement")

    model_config = {
        "json_schema_extra": {
            "example": {
                "surface_reelle_bati": 80.5,
                "nombre_pieces_principales": 4,
                "longitude": 5.9072,
                "latitude": 46.1709,
                "est_maison": 1
            }
        }
    }

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="L'adresse email de l'utilisateur")
    password: str = Field(..., min_length=8, description="Le mot de passe")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "directeur@ymmo.fr",
                "password": "admin123"
            }
        }
    }

class BienCreate(BaseModel):
    titre: str = Field(..., description="Le titre de l'annonce")
    prix: float = Field(..., gt=0, description="Le prix de vente en euros")
    surface: float = Field(..., gt=0)
    pieces: int = Field(..., gt=0)
    type_bien: str = Field(..., description="Appartement ou Maison")
    ville: str = Field(...)

    model_config = {
        "json_schema_extra": {
            "example": {
                "titre": "Bel appartement lumineux",
                "prix": 250000.0,
                "surface": 65.0,
                "pieces": 3,
                "type_bien": "Appartement",
                "ville": "Lyon"
            }
        }
    }

class Bien(BienCreate):
    id: int
    est_vendu: bool = False