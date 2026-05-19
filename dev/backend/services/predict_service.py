import joblib
import os
import numpy as np
from core.logger import logger

class PredictService:
    def __init__(self, model_path: str):
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            logger.info("Modèle IA chargé avec succès.")
        else:
            self.model = None
            logger.warning(f"Modèle IA introuvable à {model_path}. La prédiction est désactivée.")

    def get_prediction(self, data: dict) -> float:
        if self.model is None:
            raise RuntimeError("Le modèle IA n'est pas disponible sur ce serveur.")
        features = np.array([[
            data['surface_reelle_bati'],
            data['nombre_pieces_principales'],
            data['longitude'],
            data['latitude'],
            data['est_maison']
        ]])
        prediction = self.model.predict(features)
        return float(prediction[0])