from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from main import app

client = TestClient(app)

# ==========================================
# TEST CATALOGUE
# ==========================================

@patch('main.get_connection')
def test_get_biens_retourne_liste(mock_get_conn):
    mock_df = pd.DataFrame([{
        'id_mutation': '1', 
        'type_local': 'Appartement', 
        'valeur_fonciere': 100000, 
        'surface_reelle_bati': 50, 
        'nombre_pieces_principales': 2
    }])
    mock_conn = mock_get_conn.return_value
    mock_conn.execute.return_value.df.return_value = mock_df

    response = client.get("/api/biens")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_creation_nouveau_bien():
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

@patch('main.auth_service.authenticate')
@patch('main.insert_log')
def test_login_succes_cree_cookie(mock_insert_log, mock_auth):
    mock_auth.return_value = {"email": "directeur@ymmo.fr", "pole": "Direction"}
    
    credentials = {"email": "directeur@ymmo.fr", "password": "admin123"}
    response = client.post("/api/auth/login", json=credentials)
    
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert response.json()["email"] == "directeur@ymmo.fr"

@patch('main.auth_service.authenticate')
@patch('main.insert_log')
def test_login_echec_mauvais_mdp(mock_insert_log, mock_auth):
    mock_auth.return_value = None
    
    credentials = {"email": "directeur@ymmo.fr", "password": "fauxmotdepasse"}
    response = client.post("/api/auth/login", json=credentials)
    
    assert response.status_code == 401

def test_route_protegee_sans_cookie():
    client.cookies.clear()
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401

def test_acces_admin_sans_droits():
    client.cookies.clear()
    response = client.get("/api/admin/reports")
    
    assert response.status_code == 401