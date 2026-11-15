import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.anyio
async def test_get_posts_success(tmp_path, monkeypatch):
    """Verifica de forma asíncrona que el endpoint devuelva la lista de posts ordenada"""
    posts_dir = tmp_path / "posts"
    en_dir = posts_dir / "en"
    en_dir.mkdir(parents=True)
    
    # Crear archivo markdown de prueba temporal
    test_file = en_dir / "test-phd.md"
    post_content = "---\ntitle: Test PhD Journey\ndate: 2022-02-28\nauthor: Fabricio\n---\n\nHello world!"
    test_file.write_text(post_content, encoding="utf-8")
    
    # Mockear la ruta POSTS_DIR en el router
    import app.api.posts as posts_router
    monkeypatch.setattr(posts_router, "POSTS_DIR", posts_dir)

    # Uso de AsyncClient con transporte ASGI
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/posts/en")
        
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["slug"] == "test-phd"
    assert data[0]["title"] == "Test PhD Journey"


@pytest.mark.anyio
async def test_get_post_detail_success(tmp_path, monkeypatch):
    """Verifica de forma asíncrona el detalle y contenido HTML de un post"""
    posts_dir = tmp_path / "posts"
    en_dir = posts_dir / "en"
    en_dir.mkdir(parents=True)
    
    test_file = en_dir / "test-phd.md"
    test_file.write_text("---\ntitle: Test PhD Journey\ndate: 2022-02-28\n---\n\nHello world!", encoding="utf-8")
    
    import app.api.posts as posts_router
    monkeypatch.setattr(posts_router, "POSTS_DIR", posts_dir)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/posts/en/test-phd")
        
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "test-phd"
    assert "<p>Hello world!</p>" in data["content_html"]


@pytest.mark.anyio
async def test_get_posts_invalid_language():
    """Verifica el manejo de errores para idiomas no soportados de forma asíncrona"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/posts/fr")
        
    assert response.status_code == 404
    assert response.json()["detail"] == "Idioma no soportado"