import pytest
from bson import ObjectId

# -----------------------------------------------------------------------------
# 1. Pruebas para About Me (POST / PUT / DELETE)
# -----------------------------------------------------------------------------

# POST VALID
@pytest.mark.asyncio
async def test_create_aboutme(client, auth_headers, sample_aboutme_payload):
    """Prueba la creacion de un objecto en el documento 'About Me'"""

    create_response = await client.post(
        "/api/v1/portfolio/about_me",
        json=sample_aboutme_payload,
        headers=auth_headers
    )

    assert create_response.status_code == 201
    created_data = create_response.json()
    assert created_data["languages"][0]["name"]["en"] == "Spanish"
    assert created_data["cv_filename"] == "cv2.pdf"

# POST INVALID
@pytest.mark.asyncio
async def test_create_aboutme_invalid(client, auth_headers):
    """Prueba el intento de creacion de un objecto en el documento 'About Me' sin autenticacion"""

    bad_payload = {"languages":{"name":"English"}}

    create_response = await client.post(
        "/api/v1/portfolio/about_me",
        json=bad_payload,
        headers=auth_headers
    )

    assert create_response.status_code == 422


# PUT
@pytest.mark.asyncio
async def test_update_aboutme(client, auth_headers):
    """Prueba una actualizacion de un objecto 'About Me'"""

    # 1. Lee el unico objeto en el documento 'About Me'
    aboutme_response = await client.get(
        "/api/v1/portfolio/about_me"
    )

    assert aboutme_response.status_code == 200

    # 2. Obtenemos el objecto json
    aboutme_data = aboutme_response.json()
    assert "languages" in aboutme_data

    # 3. Obtenemos el ID
    aboutme_id = aboutme_data.get("_id")

    # 4. Realizamos una actualizacion al objecto
    aboutme_data["languages"].append(
        {
            "name": {
                "en": 'Spanish',
                "es": 'Español'
            },
            "level": {
                "en": 'Advanced',
                "es": 'Avanzado'
            },
            "note": {
                "en": '',
                "es": ''
            }
        }
    )

    # 5. Realizamos el update en la base de datos mock mediante el endpoint
    aboutme_update = await client.put(
        f"/api/v1/portfolio/about_me/{aboutme_id}",
        json=aboutme_data,
        headers=auth_headers
    )

    assert aboutme_update.status_code == 200

# -----------------------------------------------------------------------------
# 2. Pruebas para Projects (POST / PUT / DELETE)
# -----------------------------------------------------------------------------

# POST VALID
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


# POST INVALID
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


#UPDATE VALID
@pytest.mark.asyncio
async def test_update_project(client, auth_headers):
    """Prueba la eliminacion de un nuevo proyecto"""
    
    # 1. Crear el proyecto (Protegido)
    create_response = await client.get(
        "/api/v1/portfolio/projects"
    )
    assert create_response.status_code == 200

    # 2. Extrae el unico objeto en la lista de proyectos y su ID 
    updated_project = create_response.json()[0]
    project_id = updated_project.get("_id")

    # 3. Realizamos una actualizacion del objecto
    updated_project["translations"]["en"]["description"] = "FastAPI and GPT Backend"
    updated_project["translations"]["es"]["description"] = "Backend en FastAPI y GPT"

    # 2. Realizamos el update del objecto en la base de datos mock
    update_response = await client.put(
        f"/api/v1/portfolio/projects/{project_id}",
        json=updated_project,
        headers=auth_headers
    )

    assert update_response.status_code == 200


# DELETE VALID
@pytest.mark.asyncio
async def test_delete_project(client, auth_headers):
    """Prueba la eliminacion de un nuevo proyecto"""
    
    # 1. Lee el proyecto
    create_response = await client.get(
        "/api/v1/portfolio/projects"
    )
    assert create_response.status_code == 200

    # 2. Extraemos el _id del unico objecto en la lista de proyectos de la base de datos mock
    project_id = create_response.json()[0].get("_id")

    # 3. Eliminar usando el ObjectId de MongoDB
    delete_response = await client.delete(
        f"/api/v1/portfolio/projects/{project_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 204

# -----------------------------------------------------------------------------
# 6. Pruebas para Portfolio Global (GET, PUT)
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
                                       auth_headers):
    """Elimina la lista de skills y social media links del portfolio global"""

    delete_response = await client.delete(
        "/api/v1/portfolio/global",
        headers=auth_headers
    )

    assert delete_response.status_code == 204

