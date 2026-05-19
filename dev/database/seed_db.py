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
    
    # Remplacement de read_csv_auto par read_parquet
    db.execute(f"""
        CREATE TABLE ventes AS 
        SELECT * FROM read_parquet('{parquet_path}')
    """)
    
    result = db.execute("SELECT COUNT(*) FROM ventes").fetchone()
    print(f"Importation terminee : {result[0]} lignes importees depuis le Parquet avec succès.")
    
    db.close()

if __name__ == "__main__":
    import_real_data()