import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ymmo_analytics.duckdb')

def seed_users():
    db = duckdb.connect(DB_PATH)
    
    db.execute("""
    CREATE SEQUENCE IF NOT EXISTS seq_users_id;
    
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER DEFAULT nextval('seq_users_id') PRIMARY KEY,
        email VARCHAR UNIQUE,
        password_hash VARCHAR,
        pole VARCHAR
    );
    """)
    
    db.execute("""
    INSERT INTO utilisateurs (email, password_hash, pole)
    VALUES (
        'directeur@ymmo.fr',
        '$argon2id$v=19$m=65536,t=3,p=4$dDMMS5OBxxm7qk+aAJYx/Q$PZ/JHKOBd9jHJQZCdQpsghnXhAiJPVaHAsJOUjDWpcI',
        'Direction'
    ) ON CONFLICT DO NOTHING;
    """)
    
    db.close()

if __name__ == "__main__":
    seed_users()