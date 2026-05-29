import duckdb
import os

def import_real_data():
    parquet_path = '../data_analysis/data/processed/dvf_clean.parquet'
    db_path = 'ymmo_analytics.duckdb'
    
    if not os.path.exists(parquet_path):
        print(f"Erreur : Le fichier {parquet_path} est introuvable.")
        return

    db = duckdb.connect(db_path)
    
    db.execute("DROP TABLE IF EXISTS ventes")
    
    db.execute(f"""
        CREATE TABLE ventes AS 
        SELECT * FROM read_parquet('{parquet_path}')
    """)
    
    result = db.execute("SELECT COUNT(*) FROM ventes").fetchone()
    print(f"Importation terminee : {result[0]} lignes importees depuis le Parquet.")

    db.execute("DROP TABLE IF EXISTS stats_globales_cache")
    db.execute("""
        CREATE TABLE stats_globales_cache AS 
        SELECT 
            COUNT(*) as total_ventes,
            AVG(valeur_fonciere) as prix_moyen,
            AVG(valeur_fonciere / NULLIF(surface_reelle_bati, 0)) as prix_m2_moyen
        FROM ventes
        WHERE surface_reelle_bati > 0
    """)
    
    db.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_biens_id;
        
        CREATE TABLE IF NOT EXISTS biens (
            id INTEGER DEFAULT nextval('seq_biens_id') PRIMARY KEY,
            titre VARCHAR,
            prix_estime FLOAT,
            surface FLOAT,
            pieces INTEGER,
            type_bien VARCHAR,
            ville VARCHAR,
            est_vendu BOOLEAN DEFAULT FALSE,
            prix_vente_final FLOAT,
            date_vente DATE
        );
    """)

    db.close()

if __name__ == "__main__":
    import_real_data()