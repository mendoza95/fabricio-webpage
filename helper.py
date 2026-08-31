import os
import locale
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def _parse_date_flexible(d):
    """
    Parsea una fecha de manera flexible. Ya no requiere pasar 'app'.
    """
    date_str = str(d)
    formats_to_try = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%B %d, %Y',
    ]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    logger.warning(f"Could not parse date '{date_str}'. Using default 1970-01-01.")
    return datetime(1970, 1, 1)

def _set_locale(lang: str):
    """Configura el idioma sin depender del objeto app."""
    try:
        if lang == 'es':
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        else:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    except locale.Error:
        logger.warning(f"Locale for '{lang}' not supported on this system. Using default.")

def load_site_data(db, lang: str) -> dict:
    """
    Carga y procesa la información pasando la instancia 'db' explícitamente.
    Esto permite pasarle una base de datos mock durante las pruebas.
    """
    db_users_coll = db['users']
    
    usuario = db_users_coll.find_one()
    if not usuario:
        raise RuntimeError("No se encontró ningún usuario configurado en la base de datos.")
    user_id = usuario['_id']

    portfolio_global = db['portfolio_global'].find_one({"user_id": user_id}) or {}
    about_doc = db['about_me'].find_one({"user_id": user_id}) or {}
    
    raw_projects = list(db['projects'].find({"user_id": user_id}))
    raw_experience = list(db['experience'].find({"user_id": user_id}))
    raw_education = list(db['education'].find({"user_id": user_id}))
    raw_publications = list(db['publications'].find({"user_id": user_id}))

    about_trans = about_doc.get('translations', {}).get(lang, {})
    about_data = {
        "title": about_trans.get('title', ''),
        "intro": about_trans.get('intro', []),
        "cv_title": about_trans.get('cv_title', ''),
        "cv_intro": about_trans.get('cv_intro', ''),
        "cv_button": about_trans.get('cv_button', ''),
        "profile_image": about_doc.get('profile_image', ''),
        "profile_image_alt": about_doc.get('profile_image_alt', {}).get(lang, ''),
        "cv_filename": about_doc.get('cv_filename', '')
    }

    projects_data = []
    for p in raw_projects:
        trans = p.get('translations', {}).get(lang, {})
        projects_data.append({
            "id": p.get('project_id'),
            "name": trans.get('name', ''),
            "description": trans.get('description', ''),
            "description_cv": trans.get('description_cv', ''),
            "image": p.get('image', ''),
            "technologies": p.get('technologies', []),
            "live_url": p.get('live_url', ''),
            "github_urls": p.get('github_urls', [])
        })

    experience_data = []
    for exp in raw_experience:
        trans = exp.get('translations', {}).get(lang, {})
        experience_data.append({
            "id": exp.get('experience_id'),
            "role": trans.get('role', ''),
            "company": trans.get('company', ''),
            "location": trans.get('location', ''),
            "description": trans.get('description', ''),
            "description_cv": trans.get('description_cv', ''),
            "company_logo": exp.get('company_logo', ''),
            "company_url": exp.get('company_url', ''),
            "start_date": exp.get('start_date', ''),
            "end_date": exp.get('end_date', '')
        })

    education_data = []
    for edu in raw_education:
        trans = edu.get('translations', {}).get(lang, {})
        education_data.append({
            "id": edu.get('education_id'),
            "degree": trans.get('degree', ''),
            "institution": trans.get('institution', ''),
            "location": trans.get('location', ''),
            "description": trans.get('description', ''),
            "institution_logo": edu.get('institution_logo', ''),
            "institution_url": edu.get('institution_url', ''),
            "start_year": edu.get('start_year', ''),
            "end_year": edu.get('end_year', '')
        })

    publications_data = []
    for pub in raw_publications:
        trans = pub.get('translations', {}).get(lang, {})
        publications_data.append({
            "id": pub.get('publication_id'),
            "title": trans.get('title', ''),
            "journal": trans.get('journal', ''),
            "journal_cv": trans.get('journal_cv', ''),
            "authors": pub.get('authors', ''),
            "year": pub.get('year', ''),
            "urls": pub.get('urls', [])
        })

    ui_text_data = portfolio_global.get('ui_text', {}).get(lang, {})
    social_links_data = portfolio_global.get('social_media', [])
    skills_data = portfolio_global.get('skills', [])
    languages_data = about_doc.get('languages', [])

    return {
        "about": about_data,
        "projects": projects_data,
        "experience": experience_data,
        "education": education_data,
        "publications": publications_data,
        "ui_text": ui_text_data,
        "social_links": social_links_data,
        "skills": skills_data,
        "languages": languages_data
    }