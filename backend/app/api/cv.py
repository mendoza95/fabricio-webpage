from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from weasyprint import HTML

from app.core.database import get_database

router = APIRouter(prefix="/cv", tags=["CV Generator"])

# Ajusta esta ruta según dónde ubiques tu carpeta templates
templates = Jinja2Templates(directory="app/templates")


def format_doc(doc: dict | None) -> dict | None:
    if not doc:
        return None
    formatted = doc.copy()
    if "_id" in formatted and isinstance(formatted["_id"], ObjectId):
        formatted["_id"] = str(formatted["_id"])
    return formatted


@router.get("/pdf/{lang}")
async def generate_cv_pdf(lang: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Genera y devuelve el Currículum Vitae en formato PDF según el idioma ('es' o 'en')."""
    if lang not in ["en", "es"]:
        raise HTTPException(status_code=404, detail="Idioma no soportado. Usa 'es' o 'en'.")

    try:
        # 1. Consultar las colecciones de MongoDB (aplicando los ordenamientos definidos)
        about_doc = await db["about_me"].find_one()
        about = format_doc(about_doc) if about_doc else {}

        projects = [format_doc(p) for p in await db["projects"].find().to_list(100)]
        experience = [
            format_doc(e)
            for e in await db["experience"].find().sort([("end_date", -1), ("start_date", 1)]).to_list(100)
        ]
        education = [
            format_doc(e)
            for e in await db["education"].find().sort([("end_year", -1), ("start_year", 1)]).to_list(100)
        ]
        publications = [format_doc(p) for p in await db["publications"].find().to_list(100)]

        global_doc = await db["portfolio_global"].find_one()
        global_data = format_doc(global_doc) if global_doc else {}

        # 👈 PROCESAR LAS HABILIDADES SEGÚN EL IDIOMA
        raw_skills = global_data.get("skills", [])
        formatted_skills = []
        for skill in raw_skills:
            if isinstance(skill, dict):
                # Extrae el texto según el idioma, con fallback a 'en' o al primer valor disponible
                formatted_skills.append(skill.get(lang) or skill.get("en") or next(iter(skill.values()), ""))
            elif isinstance(skill, str):
                formatted_skills.append(skill)

        ui_doc = await db["ui_translations"].find_one()
        ui_text = ui_doc.get(lang, {}) if ui_doc else {}

        # 2. Preparar contextos adaptados a la plantilla cv.html
        about_trans = about.get("translations", {}).get(lang, {})
        about_context = {
            "title": about_trans.get("cv_title") or about_trans.get("title", ""),
            "intro": about_trans.get("cv_intro") or about_trans.get("intro", []),
        }

        formatted_projects = [
            {
                "name": p.get("translations", {}).get(lang, {}).get("name", ""),
                "technologies_cv": p.get("technologies", []),
                "github_urls": p.get("github_urls", []),
                "description_cv": p.get("translations", {}).get(lang, {}).get("description_cv", []),
            }
            for p in projects
        ]

        formatted_experience = [
            {
                "role": e.get("translations", {}).get(lang, {}).get("role", ""),
                "company": e.get("translations", {}).get(lang, {}).get("company", ""),
                "location": e.get("translations", {}).get(lang, {}).get("location", ""),
                "start_date": e.get("start_date", ""),
                "end_date": e.get("end_date", "") or ("Present" if lang == "en" else "Presente"),
                "description_cv": e.get("translations", {}).get(lang, {}).get("description_cv", []),
            }
            for e in experience
        ]

        formatted_education = [
            {
                "degree": ed.get("translations", {}).get(lang, {}).get("degree", ""),
                "institution": ed.get("translations", {}).get(lang, {}).get("institution", ""),
                "location": ed.get("translations", {}).get(lang, {}).get("location", ""),
                "start_year": ed.get("start_year", ""),
                "end_year": ed.get("end_year", ""),
            }
            for ed in education
        ]

        formatted_publications = [
            {
                "title": pub.get("translations", {}).get(lang, {}).get("title", ""),
                "year": pub.get("year", ""),
                "urls": pub.get("urls", []),
                "journal_cv": pub.get("translations", {}).get(lang, {}).get("journal", ""),
            }
            for pub in publications
        ]

        # 3. Renderizar HTML y convertir a PDF
        template = templates.get_template("cv.html")
        rendered_html = template.render(
            lang=lang,
            about=about_context,
            ui_text=ui_text,
            education=formatted_education,
            experience=formatted_experience,
            projects=formatted_projects,
            publications=formatted_publications,
            social_links=global_data.get("social_media", []),
            skills=formatted_skills,
            languages=global_data.get("languages", []),
        )

        pdf_bytes = HTML(string=rendered_html).write_pdf()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="Fabricio_Mendoza_CV_{lang.upper()}.pdf"'
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")