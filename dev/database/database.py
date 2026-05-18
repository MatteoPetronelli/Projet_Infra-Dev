import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/ymmo_analytics.duckdb')

def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

def get_stats_globales():
    conn = get_connection()
    try:
        query = """
            SELECT 
                COUNT(*) as total_ventes,
                AVG(valeur_fonciere) as prix_moyen,
                AVG(valeur_fonciere / NULLIF(surface_reelle_bati, 0)) as prix_m2_moyen
            FROM ventes
            WHERE surface_reelle_bati > 0
        """
        return conn.execute(query).df().to_dict(orient='records')[0]
    finally:
        conn.close()

def get_user_by_email(email: str):
    conn = get_connection()
    try:
        query = "SELECT * FROM utilisateurs WHERE email = ?"
        result = conn.execute(query, [email]).df().to_dict(orient='records')
        if len(result) > 0:
            return result[0]
        return None
    finally:
        conn.close()

def insert_log(utilisateur: str, action: str, ip: str):
    conn = duckdb.connect(DB_PATH)
    try:
        conn.execute("""
        INSERT INTO logs (utilisateur, action, ip)
        VALUES (?, ?, ?)
        """, [utilisateur, action, ip])
    finally:
        conn.close()

def get_all_logs():
    conn = get_connection()
    try:
        query = """
        SELECT 
            id, 
            strftime(timestamp, '%Y-%m-%d %H:%M:%S') as timestamp, 
            utilisateur as user, 
            action, 
            ip 
        FROM logs 
        ORDER BY id DESC
        """
        return conn.execute(query).df().to_dict(orient='records')
    finally:
        conn.close()