import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ymmo_analytics.duckdb')

def seed_biens():
    db = duckdb.connect(DB_PATH)
    
    db.execute("CREATE SEQUENCE IF NOT EXISTS seq_biens_id;")
    db.execute("""
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
    
    db.execute("DELETE FROM biens;")
    
    biens_data = [
        ('Magnifique T3 Lumineux', 245000.0, 68.5, 3, 'Appartement', 'Lyon', False, None, None),
        ('Studio Etudiant Centre-Ville', 95000.0, 22.0, 1, 'Appartement', 'Nantes', False, None, None),
        ('Maison Contemporaine avec Jardin', 420000.0, 140.0, 5, 'Maison', 'Bordeaux', False, None, None),
        ('Villa d Architecte Piscine', 890000.0, 210.0, 7, 'Maison', 'Marseille', False, None, None),
        ('Duplex Renove Vieux Port', 320000.0, 75.0, 4, 'Appartement', 'Marseille', True, 315000.0, '2026-04-15'),
        ('Pavillon Familial Calme', 280000.0, 110.0, 5, 'Maison', 'Lyon', True, 280000.0, '2026-05-10')
    ]
    
    for bien in biens_data:
        db.execute("""
        INSERT INTO biens (titre, prix_estime, surface, pieces, type_bien, ville, est_vendu, prix_vente_final, date_vente)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, bien)
        
    db.close()
    print("Seed des biens termine avec succes.")

if __name__ == "__main__":
    seed_biens()