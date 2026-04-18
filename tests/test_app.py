import pytest
from app import app, compiler_ingredients

@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_recettes(mocker):
    recettes_data = [
        {
            "nom": "Recette 1",
            "portions": 2,
            "ingredients": [
                {"nom": "Tomate", "quantite": 2, "unite": "pièce"},
                {"nom": "Oignon", "quantite": 1, "unite": "pièce"}
            ]
        },
        {
            "nom": "Recette 2",
            "portions": 4,
            "ingredients": [
                {"nom": "Tomate", "quantite": 3, "unite": "pièce"},
                {"nom": "Ail", "quantite": 2, "unite": "gousse"}
            ]
        }
    ]
    mocker.patch("app.charger_recettes", return_value=recettes_data)
    return recettes_data

def test_api_compiler_happy_path(client, mock_recettes):
    response = client.post("/api/compiler", json={"indices": [0, 1]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["recettes"] == ["Recette 1", "Recette 2"]

    # Check that ingredients are compiled and deduplicated correctly
    # Tomates: 2 + 3 = 5 pièce
    # Oignon: 1 pièce
    # Ail: 2 gousse
    liste = data["liste"]
    assert len(liste) == 3

    # We can check specific items
    tomates = next((item for item in liste if item["nom"].lower() == "tomate"), None)
    assert tomates is not None
    assert tomates["quantite"] == 5
    assert tomates["unite"] == "pièce"

    # Text export should be present
    assert "texte_export" in data
    assert "🛒 LISTE DE COURSES" in data["texte_export"]

def test_api_compiler_no_selection(client, mock_recettes):
    response = client.post("/api/compiler", json={"indices": []})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Aucune recette sélectionnée"

def test_api_compiler_out_of_bounds_indices(client, mock_recettes):
    response = client.post("/api/compiler", json={"indices": [999, -1]})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Aucune recette sélectionnée"

def test_api_compiler_missing_indices_key(client, mock_recettes):
    response = client.post("/api/compiler", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"] == "Aucune recette sélectionnée"
