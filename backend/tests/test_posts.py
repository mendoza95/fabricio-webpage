import os
from pathlib import Path
import frontmatter
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def tmp_post_setup(tmp_path, monkeypatch):
    """Fixture auxiliar para crear un post de prueba temporal"""
    posts_dir = tmp_path / "posts"
    en_dir = posts_dir / "en"
    en_dir.mkdir(parents=True)
    
    # Crear un archivo markdown de prueba
    test_file = en_dir / "test-phd.md"
    post_content = "---\ntitle: Test PhD Journey\ndate: 2022-02-28\nauthor: Fabricio\n---\n\nHello world!"
    test_file.write_text(post_content, encoding="utf-8")
    
    # Modificar temporalmente la ruta POSTS_DIR en el router de posts
    import app.api.posts as posts_router
    monkeypatch.setattr(posts_router, "POSTS_DIR", posts_dir)


def test_get_posts_success(tmp_path, monkeypatch):
    """Verifica que el endpoint devuelva la lista de posts correctamente ordenada"""
    tmp_post_setup(tmp_path, monkeypatch)

    response = client.get("/api/v1/posts/en")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["slug"] == "test-phd"
    assert data[0]["title"] == "Test PhD Journey"


def test_get_post_detail_success(tmp_path, monkeypatch):
    """Verifica que se pueda obtener el detalle y el contenido HTML de un post específico"""
    tmp_post_setup(tmp_path, monkeypatch)

    response = client.get("/api/v1/posts/en/test-phd")
    assert response.status_code == 200
    data = response.json()

    assert data["slug"] == "test-phd"
    assert data["title"] == "Test PhD Journey"
    assert "<p>Hello world!</p>" in data["content_html"]


def test_get_posts_invalid_language():
    """Verifica que devuelva 404 si se solicita un idioma no soportado"""
    response = client.get("/api/v1/posts/fr")
    assert response.status_code == 404
    assert response.json()["detail"] == "Idioma no soportado"


def test_get_post_detail_not_found(tmp_path, monkeypatch):
    """Verifica que devuelva 404 si el post no existe"""
    posts_dir = tmp_path / "posts"
    (posts_dir / "en").mkdir(parents=True)
    
    import app.api.posts as posts_router
    monkeypatch.setattr(posts_router, "POSTS_DIR", posts_dir)

    response = client.get("/api/v1/posts/en/post-que-no-existe")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post no encontrado"