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
async def test_get_portfolio_global_authenticated(client, auth_headers):
    """Endpoint protegido de configuración global."""
    response = await client.get("/api/v1/portfolio/global", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "social_media" in data

@pytest.mark.asyncio
async def test_get_portfolio_global_unauthorized(client):
    """Acceso denegado a configuración global sin token JWT."""
    response = await client.get("/api/v1/portfolio/global")
    assert response.status_code == 401