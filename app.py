import os

from flask import Flask, render_template, redirect, session, url_for, flash, request, get_flashed_messages, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone # Keep datetime for inject_now and post sorting
from dotenv import load_dotenv
from weasyprint import HTML
from flask_login import LoginManager
from pymongo import MongoClient
from bcrypt import checkpw
from flask_flatpages import FlatPages, pygments_style_defs
from bson.objectid import ObjectId
from auth import get_db_collection

# Import helper functions
from helper import _parse_date_flexible, _set_locale, load_site_data

load_dotenv(override=True)  # Force loading from .env, overriding existing env vars.

# 1. IMPORTA el blueprint y la función de carga desde tu nuevo archivo
from auth import auth_bp, load_user_from_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # <-- OJO: Ahora apunta a auth.login

# 2. CONECTA el user_loader usando la función importada
@login_manager.user_loader
def load_user(user_id):
    return load_user_from_db(user_id)

# 3. REGISTRA el Blueprint en la aplicación
app.register_blueprint(auth_bp)


# Configuration for Flask-FlatPages
app.config['FLATPAGES_EXTENSION'] = '.md'
app.config['FLATPAGES_ROOT'] = 'posts'
app.config['FLATPAGES_AUTO_RELOAD'] = True
app.config['FLATPAGES_META_PARSERS'] = { # Pass app to the helper function
    'date': lambda d: _parse_date_flexible(app, d)
}
flatpages = FlatPages(app)

@app.context_processor
def inject_now():
    """Injects the current year into all templates."""
    return {'now': datetime.now(timezone.utc)}

# Default route redirects to English or the session language if set
@app.route('/')
def default():
    lang = session.get('lang', 'en')
    return redirect(f'/{lang}/')

# Route to set language in session and redirect back
@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    # Redirect to the referring page or home if not available
    # For a single-page app, always redirect to the root for the new language.
    return redirect(url_for('index', lang=lang))

@app.route('/<lang>/')
def index(lang):
    if lang not in ['en', 'es']:
        return "Language not supported", 404

    _set_locale(app, lang) # Pass app instance

    session['lang'] = lang

    # --- Load all site data from JSON files ---
    try:
        site_data = load_site_data(app, lang) # Pass app instance
    except FileNotFoundError:
        return f"Data file for language '{lang}' not found.", 404

    # --- Fetch latest blog posts for the news section ---
    all_posts = [p for p in flatpages if p.path.startswith(lang + '/') and 'date' in p.meta]
    # Sort by the 'date' attribute, which is now a datetime object
    all_posts.sort(key=lambda item: item.meta['date'], reverse=True)
    latest_posts = all_posts[:3]  # Show the 3 most recent posts

    # Pass all the prepared data to the index.html template
    # Render the single, unified index.html template
    return render_template('index.html',
                           lang=lang,
                           about=site_data['about'],
                           projects=site_data['projects'],
                           education=site_data['education'],
                           experience=site_data['experience'],
                           ui_text=site_data['ui_text'],
                           latest_posts=latest_posts,
                           publications=site_data['publications'],
                           social_links=site_data['social_links'])

@app.route('/<lang>/cv/pdf')
def generate_cv_pdf(lang):
    """Generates a PDF version of the CV."""
    if lang not in ['en', 'es']:
        return "Language not supported", 404

    _set_locale(app, lang) # Pass app instance

    try:
        site_data = load_site_data(app, lang) # Pass app instance
    except FileNotFoundError:
        return f"Data file for language '{lang}' not found.", 404

    # Use CV-specific profile text if available to ensure a professional tone
    if 'cv_title' in site_data['about']:
        site_data['about']['title'] = site_data['about']['cv_title']
    if 'cv_intro' in site_data['about']:
        site_data['about']['intro'] = site_data['about']['cv_intro']

    # Render the CV HTML template with the necessary data
    rendered_html = render_template('cv.html',
                                    lang=lang,
                                    about=site_data['about'],
                                    ui_text=site_data['ui_text'],
                                    education=site_data['education'],
                                    experience=site_data['experience'],
                                    projects=site_data['projects'],
                                    publications=site_data['publications'],
                                    social_links=site_data['social_links'],
                                    skills=site_data.get('skills', []),
                                    languages=site_data.get('languages', []))

    # Use WeasyPrint to generate the PDF from the rendered HTML
    pdf = HTML(string=rendered_html).write_pdf()

    # Return the PDF as a downloadable file
    return pdf, 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline; filename="Fabricio_Mendoza_CV.pdf"'
    }


@app.route('/<lang>/blog/')
def blog(lang):
    session['lang'] = lang
    _set_locale(app, lang)
    
    # Reemplazamos la apertura de archivo JSON local por load_site_data
    site_data = load_site_data(app, lang)
    ui_text = site_data['ui_text']
    
    posts = [p for p in flatpages if p.path.startswith(lang + '/') and 'date' in p.meta]
    posts.sort(key=lambda item: item.meta['date'], reverse=True)
    return render_template('blog.html', lang=lang, posts=posts, ui_text=ui_text)


@app.route('/<lang>/blog/<path:path>/')
def post(lang, path):
    session['lang'] = lang
    _set_locale(app, lang)
    
    # Reemplazamos la apertura de archivo JSON local por load_site_data
    site_data = load_site_data(app, lang)
    ui_text = site_data['ui_text']
    
    full_path = f'{lang}/{path}'
    post = flatpages.get_or_404(full_path)
    return render_template('post.html', lang=lang, post=post, ui_text=ui_text)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}

@app.route('/api/update-portfolio', methods=['POST'])
@login_required # Seguridad: Solo tú autenticado puedes ejecutar esta ruta
def update_portfolio():
    data = request.get_json()

    collection_name = data.get('collection')
    doc_id = data.get('id')
    field = data.get('field')
    lang = data.get('lang')
    nuevo_texto = data.get('text')

    if not collection_name or not field or not lang:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    # Obtener la conexión a la base de datos
    db_users = get_db_collection()
    db = db_users.database
    collection = db[collection_name]

    user_id = current_user.id # Asegurar que editamos los datos de TU usuario

    try:
        # CASO 1: Documento único por usuario (about_me, portfolio_global)
        if collection_name in ['about_me', 'portfolio_global']:
            campo_a_actualizar = f"translations.{lang}.{field}"
            
            # Para el título o intro de about_me
            result = collection.update_one(
                {"user_id": user_id},
                {"$set": {campo_a_actualizar: nuevo_texto}}
            )

        # CASO 2: Documentos en colecciones con ID propio (projects, experience, education, publications)
        else:
            # Determinamos cuál es la clave identificadora según la colección
            id_key_map = {
                'projects': 'project_id',
                'experience': 'experience_id',
                'education': 'education_id',
                'publications': 'publication_id'
            }
            
            id_key = id_key_map.get(collection_name)
            campo_a_actualizar = f"translations.{lang}.{field}"

            result = collection.update_one(
                {"user_id": user_id, id_key: doc_id},
                {"$set": {campo_a_actualizar: nuevo_texto}}
            )

        if result.modified_count > 0 or result.matched_count > 0:
            return jsonify({"status": "success", "message": "Actualizado correctamente"})
        else:
            return jsonify({"status": "error", "message": "No se encontró el registro para actualizar"}), 404

    except Exception as e:
        app.logger.error(f"Error actualizando la BD: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
