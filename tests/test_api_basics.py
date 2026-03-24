import os

os.environ.setdefault("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/booksmart")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_AUTH_DISABLED", "true")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint_returns_active_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to backend", "status": "active"}


def test_docs_endpoint_is_available():
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_openapi_contains_expected_metadata_for_local_auth_mode():
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert schema["info"]["title"] == "Booksmart Backend API"
    assert schema.get("x-auth-mode") == "jwt-disabled-local"
