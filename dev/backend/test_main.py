import pytest
import os
import duckdb
from fastapi.testclient import TestClient
from main import app
import database.database as db_module
from dependencies import get_current_user

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_ymmo_analytics.duckdb")

# ==========================================
# CONFIGURATION & INITIALIZATION (FIXTURE)
# ==========================================

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
            password_hash VARCHAR,
            pole VARCHAR
        )
    """)
    conn.execute("""
        INSERT INTO utilisateurs VALUES 
        ('directeur@ymmo.fr', 'hashed_pwd', 'Direction'),
        ('it@ymmo.fr', 'hashed_pwd', 'IT et Support'),
        ('user@ymmo.fr', 'hashed_pwd', 'Utilisateur')
    """)
    
    conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_biens_id")
    conn.execute("""
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
        )
    """)
    conn.execute("""
        INSERT INTO biens (titre, prix_estime, surface, pieces, type_bien, ville, est_vendu, prix_vente_final, date_vente)
        VALUES 
        ('Appartement Ancien', 200000.0, 60.0, 3, 'Appartement', 'Paris', FALSE, NULL, NULL),
        ('Maison Vendue', 350000.0, 100.0, 4, 'Maison', 'Lyon', TRUE, 340000.0, '2026-05-01')
    """)
    
    conn.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_logs_id;
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER DEFAULT nextval('seq_logs_id') PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
# CATALOG TESTS (PROPERTIES & SALES)
# ==========================================

def test_get_properties_returns_list():
    with TestClient(app) as client:
        response = client.get("/api/biens")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 2

def test_create_new_property():
    app.dependency_overrides[get_current_user] = lambda: {"email": "directeur@ymmo.fr", "pole": "Direction"}
    with TestClient(app) as client:
        new_property = {
            "titre": "Appartement Test Unitaire",
            "prix": 150000.0,
            "surface": 45.0,
            "pieces": 2,
            "type_bien": "Appartement",
            "ville": "Nantes"
        }
        response = client.post("/api/biens", json=new_property)
        assert response.status_code == 200
        assert response.json()["titre"] == "Appartement Test Unitaire"
        assert response.json()["id"] is not None
    app.dependency_overrides.clear()

def test_sell_property():
    app.dependency_overrides[get_current_user] = lambda: {"email": "directeur@ymmo.fr", "pole": "Direction"}
    with TestClient(app) as client:
        response = client.post("/api/biens/1/vendre", json={"prix_vente_final": 195000.0})
        assert response.status_code == 200
        assert response.json()["prix_final"] == 195000.0
    app.dependency_overrides.clear()

def test_sell_already_sold_property():
    app.dependency_overrides[get_current_user] = lambda: {"email": "directeur@ymmo.fr", "pole": "Direction"}
    with TestClient(app) as client:
        response = client.post("/api/biens/2/vendre", json={"prix_vente_final": 340000.0})
        assert response.status_code == 400
    app.dependency_overrides.clear()

# ==========================================
# DASHBOARD TESTS (REPORTING & ANALYTICS)
# ==========================================

def test_admin_reports():
    app.dependency_overrides[get_current_user] = lambda: {"email": "directeur@ymmo.fr", "pole": "Direction"}
    with TestClient(app) as client:
        response = client.get("/api/admin/reports")
        assert response.status_code == 200
        data = response.json()
        assert "performances" in data
        assert "volume_global" in data
    app.dependency_overrides.clear()

def test_admin_analysis():
    app.dependency_overrides[get_current_user] = lambda: {"email": "directeur@ymmo.fr", "pole": "Direction"}
    with TestClient(app) as client:
        response = client.get("/api/admin/analysis")
        assert response.status_code == 200
        assert "tendances_globales" in response.json()
    app.dependency_overrides.clear()

# ==========================================
# SECURITY & RBAC TESTS (ACCESS RIGHTS)
# ==========================================

def test_it_cannot_promote_to_direction():
    app.dependency_overrides[get_current_user] = lambda: {"email": "it@ymmo.fr", "pole": "IT et Support"}
    with TestClient(app) as client:
        response = client.put("/api/admin/users/role", json={"email": "user@ymmo.fr", "pole": "Direction"})
        assert response.status_code == 403
    app.dependency_overrides.clear()

def test_protected_route_without_cookie():
    with TestClient(app) as client:
        client.cookies.clear()
        response = client.get("/api/auth/me")
        assert response.status_code == 401

def test_admin_access_without_rights():
    with TestClient(app) as client:
        client.cookies.clear()
        response = client.get("/api/admin/reports")
        assert response.status_code == 401

# ==========================================
# API PROTECTION TESTS (RATE LIMITING)
# ==========================================

def test_rate_limiting_predict():
    with TestClient(app) as client:
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