import pytest

# -----------------------------------------------------------------------------
# 1. Pruebas para Portfolio Global (GET, PUT)
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_portfolio_global(client, 
                                                auth_headers,
                                                sample_portfolio_global_payload):
    """Verifica que un usuario no auntenticado no pueda leer la los skills"""

    post_response = await client.post("/api/v1/portfolio/global",
                                    json=sample_portfolio_global_payload,
                                    headers=auth_headers)

    assert post_response.status_code == 201

@pytest.mark.asyncio
async def test_update_portfolio_global_unauthorized(client):
    """Verifica que un usuario no autenticado no pueda actualizar la configuración global."""
    payload = {
        "skills": [{"en": "Python", "es": "Python"}],
        "social_media": []
    }
    response = await client.put("/api/v1/portfolio/global", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_portfolio_global_success(client, auth_headers):
    """Verifica que un usuario autenticado pueda actualizar la configuración global."""
    payload = {
        "skills": [{"en": "FastAPI Master", "es": "FastAPI Maestro"}],
        "social_media": [
            {"name": "LinkedIn", "url": "https://linkedin.com", "username": "dev", "icon_svg": "<svg></svg>"}
        ]
    }
    response = await client.put("/api/v1/portfolio/global", json=payload, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["skills"][0]["en"] == "FastAPI Master"
    assert len(data["social_media"]) == 1

@pytest.mark.asyncio
async def test_delete_portfolio_global(client,
                                       sample_portfolio_global_payload, 
                                       auth_headers):
    """Elimina la lista de skills y social media links del portfolio global"""
    create_response = await client.post(
        "/api/v1/portfolio/global",
        json=sample_portfolio_global_payload,
        headers=auth_headers
    )

    assert create_response.status_code == 201

    print(create_response.json())
    global_id = create_response.json().get("id")
    print(global_id)

    delete_response = await client.delete(
        "/api/v1/portfolio/global/{global_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 204

# -----------------------------------------------------------------------------
# 2. Pruebas para Projects (POST / GET / DELETE)
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_project(client, auth_headers, sample_project_payload):
    """Prueba la creación de un nuevo proyecto y su posterior consulta."""

    # 1. Crear el proyecto (Protegido)
    create_response = await client.post(
        "/api/v1/portfolio/projects", 
        json=sample_project_payload, 
        headers=auth_headers
    )
    assert create_response.status_code in [200, 201]
    created_data = create_response.json()
    assert created_data["translations"]["es"]["name"] == "Portafolio Personal"
    assert "id" in created_data or "_id" in created_data

@pytest.mark.asyncio
async def test_create_project_invalid_payload(client, auth_headers):
    """Verifica que Pydantic rechace la creación si faltan campos obligatorios."""
    bad_payload = {
        "translations": "No valid input" 
    }
    response = await client.post(
        "/api/v1/portfolio/projects", 
        json=bad_payload, 
        headers=auth_headers
    )
    # Debe retornar 422 Unprocessable Entity por falla de validación de Pydantic
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_and_delete_project(client, auth_headers, sample_project_payload):
    """Prueba la eliminacion de un nuevo proyecto"""
    
    # 1. Crear el proyecto (Protegido)
    create_response = await client.post(
        "/api/v1/portfolio/projects", 
        json=sample_project_payload, 
        headers=auth_headers
    )
    assert create_response.status_code in [200, 201]

    # Extraer el ID real generado por MongoDB (usualmente mapeado como "id" o "_id")
    project_id = create_response.json().get("id")

    # 2. Eliminar usando el ObjectId real de MongoDB
    delete_response = await client.delete(
        f"/api/v1/portfolio/projects/{project_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_create_and_update_project(client, auth_headers, sample_project_payload):
    """Prueba la eliminacion de un nuevo proyecto"""
    
    # 1. Crear el proyecto (Protegido)
    create_response = await client.post(
        "/api/v1/portfolio/projects", 
        json=sample_project_payload, 
        headers=auth_headers
    )
    assert create_response.status_code in [200, 201]

    # Extraer el ID real generado por MongoDB (usualmente mapeado como "id" o "_id")
    project_id = create_response.json().get("id")

    updated_project = sample_project_payload
    updated_project["translations"]["en"]["description"] = "FastAPI and GPT Backend"
    updated_project["translations"]["es"]["description"] = "Backend en FastAPI y GPT"

    # 2. Eliminar usando el ObjectId real de MongoDB
    update_response = await client.put(
        f"/api/v1/portfolio/projects/{project_id}",
        json=updated_project,
        headers=auth_headers
    )

    assert update_response.status_code == 200