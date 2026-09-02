def test_root_redirect(client):
    """La ruta raíz '/' debe redirigir por defecto a '/en/'."""
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/en/"


def test_index_route_not_found_without_data(client):
    """Si se pide '/en/' sin haber cargado usuario en la BD falsa, debe fallar gracefully o dar 404."""
    # Como load_site_data requiere un usuario en la BD, se ejecutará el RuntimeError/404 esperado
    response = client.get("/en/")
    assert response.status_code == 500 or response.status_code == 404


def test_index_route_success(client, mock_db):
    """Verifica que la página principal cargue status 200 OK cuando existen datos completos en la BD."""
    # 1. Insertar usuario simulado
    user_id = mock_db["users"].insert_one({"username": "fabricio"}).inserted_id

    # 2. Insertar información de 'about_me'
    mock_db["about_me"].insert_one(
        {
            "user_id": user_id,
            "translations": {"en": {"title": "Welcome", "intro": ["Hello"]}},
        }
    )

    # 3. Insertar información de 'portfolio_global' (indispensable para ui_text)
    mock_db["portfolio_global"].insert_one(
        {
            "user_id": user_id,
            "ui_text": {
                "en": {
                    "date_format": "%B %d, %Y",  # 👈 ¡ESTO ERA LO QUE FALTABA!
                    "published_on_prefix": "Published on",
                }
            },
            "social_media": [],
            "skills": [],
        }
    )

    # 4. Las colecciones de listas (projects, experience, etc.) pueden quedar vacías en la BD,
    # pero deben existir para que no fallen las búsquedas.

    # Ejecutar la petición
    response = client.get("/en/")

    # ¡Ahora sí devolverá 200 OK!
    assert response.status_code == 200
