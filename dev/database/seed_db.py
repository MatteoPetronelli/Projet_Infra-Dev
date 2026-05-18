import duckdb
import os

def import_real_data():
    csv_path = '../data_analysis/data/processed/dvf_clean.csv'
    db_path = 'ymmo_analytics.duckdb'
    
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} est introuvable.")
        return

    db = duckdb.connect(db_path)
    
    db.execute("DROP TABLE IF EXISTS ventes")
    
    db.execute(f"""
        CREATE TABLE ventes AS 
        SELECT * FROM read_csv_auto('{csv_path}')
    """)
    
    result = db.execute("SELECT COUNT(*) FROM ventes").fetchone()
    print(f"Importation terminee : {result[0]} lignes importees depuis le CSV.")
    
    db.close()

if __name__ == "__main__":
    import_real_data()