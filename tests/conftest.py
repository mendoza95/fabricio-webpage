import pytest
import mongomock
from app import create_app


@pytest.fixture
def mock_db():
    """
    Crea una base de datos en memoria simulada usando mongomock.
    Se resetea para cada test, garantizando aislamiento total.
    """
    client = mongomock.MongoClient()
    db = client["test_database"]
    return db


@pytest.fixture
def app(mock_db):
    """
    Crea una instancia de la aplicación Flask usando el patrón Factoría,
    inyectándole la base de datos falsa (mock_db).
    """
    app = create_app(
        test_config={"TESTING": True, "DB": mock_db, "SECRET_KEY": "test-key-123"}
    )
    return app


@pytest.fixture
def client(app):
    """
    Un cliente de pruebas de Flask que permite hacer solicitudes HTTP
    (GET, POST, etc.) simuladas a las rutas del servidor.
    """
    return app.test_client()
