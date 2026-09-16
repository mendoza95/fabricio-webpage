import pytest
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient
from bson import ObjectId

from app.main import app
from app.core.database import get_database  # Ajusta esta importación según donde obtienes tu cliente de BD
from app.core.security import create_access_token  # Ajusta la ruta a tu generador de tokens JWT


@pytest.fixture
async def mock_db():
    """Crea una base de datos simulada en memoria para cada test."""
    client = AsyncMongoMockClient()
    db = client["test_portfolio_db"]

    await db["users"].insert_one({
        "_id": ObjectId("60c72b2f9b1e8a2a4c8b4567"),
        "username": "admin@example.com",
        "email": "admin@example.com",
        "is_active": True
    })

    await db["projects"].insert_one({
        "project_id": "12345",
        "translations": {
            "en": {
                "name": "Personal Portfolio",
                "description": "FastAPI Backend",
            },
            "es": {
                "name": "Portafolio Personal",
                "description": "Backend en FastAPI",
            }
        },
        "technologies": ["FastAPI", "MongoDB", "React"],
        "is_featured": True
    })

    await db["experience"].insert_one({
        "experience_id": "123",
        "company_logo": "",
        "company_url": "",
        "start_date": "",
        "end_date": "",
        "translations": {
            "en":{
                "role":"",
                "company":"",
                "location":"",
                "description": [],
                "description_cv":[]
            }        
        }
    })

    # Poblar traducciones por defecto requeridas
    await db["ui_translations"].insert_one({
        "translations": {
            "en": {
                "date_format": "%B %d, %Y",
                "published_on_prefix": "Published on"
            },
            "es": {
                "date_format": "%d de %B de %Y",
                "published_on_prefix": "Publicado el"
            }
        }
    })

    # Poblar configuración global
    await db["portfolio_global"].insert_one({
        "skills": [{"en": "FastAPI", "es": "FastAPI"}],
        "social_media": [{"name": "GitHub", "url": "https://github.com", "username": "dev", "icon_svg": "<svg></svg>"}]
    })

    return db


@pytest.fixture
async def client(mock_db):
    """Cliente HTTP asíncrono para enviar peticiones a FastAPI en memoria."""
    # Sobrescribir la dependencia de la base de datos de la app
    app.dependency_overrides[get_database] = lambda: mock_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Genera cabeceras con token JWT válido para endpoints protegidos."""
    token = create_access_token(data={"sub": "admin@example.com"})
    return {"Authorization": f"Bearer {token}"}

# tests/conftest.py
import pytest

@pytest.fixture
def sample_project_payload():
    """Returns a valid dictionary payload for project CRUD operations."""
    return {
        "project_id": "12345",
        "translations": {
            "en": {
                "name": "Personal Portfolio",
                "description": "FastAPI Backend",
            },
            "es": {
                "name": "Portafolio Personal",
                "description": "Backend en FastAPI",
            }
        },
        "technologies": ["FastAPI", "MongoDB", "React"],
        "is_featured": True
    }

@pytest.fixture
def sample_portfolio_global_payload():
    """Returns a valid dictionary payload for portfolio_global CRUD operations"""
    return {
        "skills":[
            {
                "en": "Fast API",
                "es": "Fast API"
            }
        ],
        "social_media":[
            {
                "username":"user@social.media",
                "icon_svg":"some_image.png"
            }
        ]
    }