import pytest

@pytest.mark.asyncio
async def test_get_ui_translations(client):
    response = await client.get("/api/v1/portfolio/ui-translations")
    assert response.status_code == 200
    data = response.json()
    assert "translations" in data
    assert "es" in data["translations"]
    assert "en" in data["translations"]

@pytest.mark.asyncio
async def test_get_portfolio_global(client):
    """Endpoint de configuración global."""
    response = await client.get("/api/v1/portfolio/global")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "social_media" in data

@pytest.mark.asyncio
async def test_get_projects(client):
    """Endpoint de proyectos"""
    response = await client.get("/api/v1/portfolio/projects")
    assert response.status_code == 200

    data = response.json()[0] #retrieve the only project element

    assert "project_id" in data
    assert data["translations"]["en"]["name"] == "Personal Portfolio"

@pytest.mark.asyncio
async def test_get_experience(client):
    """Endpoint de Experience"""
    response = await client.get("/api/v1/portfolio/experience")
    assert response.status_code == 200

    data = response.json()[0] #retrieve the only experience element

    assert "experience_id" in data
    assert "role" in data["translations"]["en"]