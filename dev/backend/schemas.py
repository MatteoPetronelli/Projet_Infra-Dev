from pydantic import BaseModel

class BienImmobilier(BaseModel):
    surface_reelle_bati: float
    nombre_pieces_principales: int
    longitude: float
    latitude: float
    est_maison: int