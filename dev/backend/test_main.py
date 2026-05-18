from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# TEST CATALOGUE

def test_get_biens_retourne_liste():
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
    assert data["est_vendu"] == False
    assert "id" in data

# TEST AUTHENTIFICATION

def test_login_succes_cree_cookie():
    credentials = {"email": "directeur@ymmo.fr", "password": "admin123"}
    response = client.post("/api/auth/login", json=credentials)
    
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert response.json()["email"] == "directeur@ymmo.fr"

def test_login_echec_mauvais_mdp():
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