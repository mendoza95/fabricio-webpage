from pathlib import Path

import frontmatter
import markdown
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/posts", tags=["Posts & News"])

# Definimos la ruta base de la carpeta posts (ajustada a la raíz del backend)
POSTS_DIR = Path("posts")

@router.get("/{lang}")
async def get_posts(lang: str):
    """ Obtiene la lista de posts disponibles para el idioma 
        especificado ('es' o 'en'), ordenados por fecha.
    """
    if lang not in ["en", "es"]:
        raise HTTPException(status_code=404, detail="Idioma no soportado")

    lang_dir = POSTS_DIR / lang
    if not lang_dir.exists():
        return []

    posts = []
    # Leer todos los archivos .md en la carpeta correspondiente
    for file_path in lang_dir.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
                
            # El slug o identificador del post será el nombre del archivo sin extensión
            slug = file_path.stem
            
            posts.append({
                "slug": slug,
                "title": post.get("title", "Sin título"),
                "date": str(post.get("date", "")),
                "author": post.get("author", "Fabricio Mendoza"),
                "summary": post.get("summary", "")
            })
        except Exception as e:
            print(f"Error leyendo el archivo {file_path.name}: {e}")

    # Ordenar por fecha de forma descendente (más recientes primero)
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts


@router.get("/{lang}/{slug}")
async def get_post_detail(lang: str, slug: str):
    """Obtiene el contenido completo de un post específico renderizado en HTML."""
    if lang not in ["en", "es"]:
        raise HTTPException(status_code=404, detail="Idioma no soportado")

    file_path = POSTS_DIR / lang / f"{slug}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Convertir el contenido de Markdown a HTML seguro
        html_content = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])

        return {
            "slug": slug,
            "title": post.get("title", "Sin título"),
            "date": str(post.get("date", "")),
            "author": post.get("author", "Fabricio Mendoza"),
            "content_html": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el post: {e!s}")