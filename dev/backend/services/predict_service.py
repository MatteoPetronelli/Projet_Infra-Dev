import pickle
import os
import pandas as pd
from core.logger import logger

class PredictService:
    def __init__(self, model_path: str):
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Modèle IA chargé avec succès.")
        else:
            self.model = None
            logger.warning(f"Modèle IA introuvable à {model_path}. La prédiction est désactivée.")

    def get_prediction(self, data: dict) -> float:
        if self.model is None:
            raise RuntimeError("Le modèle IA n'est pas disponible sur ce serveur.")
        
        surface = data.get('surface_reelle_bati', 0)
        pieces = data.get('nombre_pieces_principales', 1)
        est_maison = data.get('est_maison', 0)
        
        is_apt = False if est_maison == 1 else True
        is_house = True if est_maison == 1 else False
        
        df = pd.DataFrame([{
            'surface': surface,
            'pieces': pieces,
            'type_bien_Appartement': is_apt,
            'type_bien_Maison': is_house
        }])
        
        prediction = self.model.predict(df)[0]
        return float(prediction)