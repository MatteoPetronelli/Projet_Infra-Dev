import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ymmo_analytics.duckdb')

def init_db():
    conn = duckdb.connect(DB_PATH)
    try:
        conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_logs_id;
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER DEFAULT nextval('seq_logs_id') PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            utilisateur VARCHAR,
            action VARCHAR,
            ip VARCHAR
        );
        """)
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()