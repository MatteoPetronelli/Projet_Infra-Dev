import joblib
import numpy as np

class PredictService:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def get_prediction(self, data: dict) -> float:
        features = np.array([[
            data['surface_reelle_bati'],
            data['nombre_pieces_principales'],
            data['longitude'],
            data['latitude'],
            data['est_maison']
        ]])
        prediction = self.model.predict(features)
        return float(prediction[0])