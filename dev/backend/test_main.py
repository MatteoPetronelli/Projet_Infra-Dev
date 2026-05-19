import pytest
import os
import duckdb
import pandas as pd
from fastapi.testclient import TestClient
from main import app
import database.database as db_module

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_ymmo_analytics.duckdb")

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    db_module.DB_PATH = TEST_DB_PATH
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    conn = duckdb.connect(TEST_DB_PATH)
    
    conn.execute("""
        CREATE TABLE ventes (
            id_mutation VARCHAR,
            type_local VARCHAR,
            valeur_fonciere DOUBLE,
            surface_reelle_bati DOUBLE,
            nombre_pieces_principales INT
        )
    """)
    conn.execute("""
        INSERT INTO ventes VALUES 
        ('1', 'Appartement', 150000.0, 50.0, 2),
        ('2', 'Maison', 300000.0, 120.0, 5)
    """)
    
    conn.execute("""
        CREATE TABLE stats_globales_cache (
            total_ventes BIGINT,
            prix_moyen DOUBLE,
            prix_m2_moyen DOUBLE
        )
    """)
    conn.execute("INSERT INTO stats_globales_cache VALUES (2, 225000.0, 2750.0)")
    
    conn.execute("""
        CREATE TABLE utilisateurs (
            email VARCHAR,
            password VARCHAR,
            pole VARCHAR
        )
    """)
    conn.execute("""
        INSERT INTO utilisateurs VALUES 
        ('directeur@ymmo.fr', '$argon2id$v=19$m=65536,t=3,p=4$OEV6S005...', 'Direction')
    """)
    
    conn.execute("""
        CREATE TABLE logs (
            id INTEGER,
            timestamp TIMESTAMP DEFAULT NOW(),
            utilisateur VARCHAR,
            action VARCHAR,
            ip VARCHAR
        )
    """)
    
    conn.close()
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

# ==========================================
# TEST CATALOGUE
# ==========================================

def test_get_biens_retourne_liste():
    client = TestClient(app)
    response = client.get("/api/biens")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_creation_nouveau_bien():
    client = TestClient(app)
    nouveau_bien = {
        "titre": "Appartement Test Unitaire",
        "prix": 150000.0,
        "surface": 45.0,
        "pieces": 2,
        "type_bien": "Appartement",
        "ville": "Nantes"
    }
    response = client.post("/api/biens", json=nouveau_bien)
    assert response.status_code == 200
    data = response.json()
    assert data["titre"] == "Appartement Test Unitaire"

# ==========================================
# TEST AUTHENTIFICATION
# ==========================================

def test_route_protegee_sans_cookie():
    client = TestClient(app)
    client.cookies.clear()
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_acces_admin_sans_droits():
    client = TestClient(app)
    client.cookies.clear()
    response = client.get("/api/admin/reports")
    assert response.status_code == 401

# ==========================================
# TEST CYBERSECURITE (RATE LIMITING)
# ==========================================

def test_rate_limiting_predict_bloque_les_requetes_excessives():
    client = TestClient(app)
    payload = {
        "surface_reelle_bati": 80,
        "nombre_pieces_principales": 4,
        "longitude": 5.9072,
        "latitude": 46.1709,
        "est_maison": 1
    }
    
    status_codes = []
    for _ in range(10):
        response = client.post("/api/predict", json=payload)
        status_codes.append(response.status_code)
        
    assert 429 in status_codes