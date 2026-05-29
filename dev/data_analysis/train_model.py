import duckdb
import pandas as pd
import xgboost as xgb
import pickle
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/ymmo_analytics.duckdb'))
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/processed/modele_ymmo.pkl'))

def train_model():
    conn = duckdb.connect(DB_PATH, read_only=True)
    
    df_dvf = conn.execute("""
        SELECT 
            valeur_fonciere as prix,
            surface_reelle_bati as surface,
            nombre_pieces_principales as pieces,
            type_local as type_bien
        FROM ventes
        WHERE valeur_fonciere > 0 
        AND surface_reelle_bati > 0 
        AND nombre_pieces_principales > 0
        AND type_local IN ('Appartement', 'Maison')
    """).df()
    
    df_agence = conn.execute("""
        SELECT 
            prix_vente_final as prix,
            surface,
            pieces,
            type_bien
        FROM biens
        WHERE est_vendu = TRUE 
        AND prix_vente_final > 0
        AND type_bien IN ('Appartement', 'Maison')
    """).df()
    
    conn.close()
    
    df_combined = pd.concat([df_dvf, df_agence], ignore_index=True)
    
    df_encoded = pd.get_dummies(df_combined, columns=['type_bien'])
    
    expected_cols = ['surface', 'pieces', 'type_bien_Appartement', 'type_bien_Maison']
    for col in expected_cols:
        if col not in df_encoded.columns:
            df_encoded[col] = False
            
    df_encoded = df_encoded[['prix'] + expected_cols]
    
    X = df_encoded.drop('prix', axis=1)
    y = df_encoded['prix']
    
    model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X, y)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    train_model()