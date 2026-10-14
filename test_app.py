import pytest
from fastapi.testclient import TestClient
from app import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Reset simulated database before every test."""
    db.clear()
    yield

# --- Basic Health & Path Validation ---

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_item_invalid_id_type():
    # Sending string instead of integer
    response = client.get("/items/invalid-id")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "item_id"]

# --- POST & Pydantic Validation ---

def test_create_item_success():
    payload = {"name": "Switch C885", "price": 4999.99, "in_stock": True}
    response = client.post("/items", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Switch C885"

def test_create_item_validation_error():
    # Price must be > 0 and name is too short
    payload = {"name": "A", "price": -10.0}
    response = client.post("/items", json=payload)
    
    assert response.status_code == 422
    errors = response.json()["detail"]
    fields_with_errors = [err["loc"][-1] for err in errors]
    assert "name" in fields_with_errors
    assert "price" in fields_with_errors

# --- Query Parameters ---

@pytest.mark.parametrize("query, limit, expected_limit", [
    ("cisco", 5, 5),
    (None, 10, 10),
])
def test_search_query_params(query, limit, expected_limit):
    params = {}
    if query:
        params["q"] = query
    if limit:
        params["limit"] = limit

    response = client.get("/search", params=params)
    assert response.status_code == 200
    assert response.json() == {"query": query, "limit": expected_limit}

# --- Headers & Security ---

def test_secure_endpoint_missing_header():
    response = client.get("/secure-endpoint")
    assert response.status_code == 401