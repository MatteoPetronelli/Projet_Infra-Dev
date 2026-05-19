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
    print(f"Importation terminee : {result[0]} lignes importees depuis le Parquet avec succès.")

    print("Création de la table de cache des statistiques globales...")
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
    print("Mise en cache terminée avec succès.")
    
    db.close()

if __name__ == "__main__":
    import_real_data()