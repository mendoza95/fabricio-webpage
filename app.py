import os
from datetime import datetime, timezone

import certifi
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_flatpages import FlatPages, pygments_style_defs
from flask_login import LoginManager, current_user, login_required
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from weasyprint import HTML

from auth import auth_bp, load_user_from_db
from helper import _parse_date_flexible, _set_locale, load_site_data


def create_app(test_config=None):
    load_dotenv(override=True)

    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "default-dev-key")

    # Configuración de la Base de Datos (Inyección de Dependencia)
    if test_config and "DB" in test_config:
        app.config["DB"] = test_config["DB"]
    else:
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            raise ValueError("¡ERROR CRÍTICO: MONGO_URI no configurada!")

        app.config["MONGO_URI"] = mongo_uri
        client = MongoClient(
            mongo_uri,
            tls=True,
            tlsCAFile=certifi.where(),
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            connect=False,  # Delay connection until actual read/write operation
            maxPoolSize=1,
        )
        app.config["DB"] = client["personal_webpage"]
        app.config["CLIENT"] = client

    # Inicializar LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return load_user_from_db(user_id)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)

    # Configuración FlatPages
    app.config["FLATPAGES_EXTENSION"] = ".md"
    app.config["FLATPAGES_ROOT"] = "posts"
    app.config["FLATPAGES_AUTO_RELOAD"] = True
    app.config["FLATPAGES_META_PARSERS"] = {"date": lambda d: _parse_date_flexible(d)}

    flatpages = FlatPages(app)

    @app.context_processor
    def inject_now():
        return {"now": datetime.now(timezone.utc)}

    @app.route("/")
    def default():
        lang = session.get("lang", "en")
        return redirect(f"/{lang}/")

    @app.route("/set_language/<lang>")
    def set_language(lang):
        session["lang"] = lang
        return redirect(url_for("index", lang=lang))

    @app.route("/<lang>/")
    def index(lang):
        if lang not in ["en", "es"]:
            return "Language not supported", 404

        _set_locale(lang)
        session["lang"] = lang

        try:
            site_data = load_site_data(app.config["DB"], lang)
        except FileNotFoundError:
            return f"Data file for language '{lang}' not found.", 404

        all_posts = [
            p for p in flatpages if p.path.startswith(lang + "/") and "date" in p.meta
        ]
        all_posts.sort(key=lambda item: item.meta["date"], reverse=True)
        latest_posts = all_posts[:3]

        return render_template(
            "index.html",
            lang=lang,
            about=site_data["about"],
            projects=site_data["projects"],
            education=site_data["education"],
            experience=site_data["experience"],
            ui_text=site_data["ui_text"],
            latest_posts=latest_posts,
            publications=site_data["publications"],
            social_links=site_data["social_links"],
        )

    @app.route("/<lang>/cv/pdf")
    def generate_cv_pdf(lang):
        if lang not in ["en", "es"]:
            return "Language not supported", 404

        _set_locale(lang)

        try:
            site_data = load_site_data(app.config["DB"], lang)
        except FileNotFoundError:
            return f"Data file for language '{lang}' not found.", 404

        if "cv_title" in site_data["about"]:
            site_data["about"]["title"] = site_data["about"]["cv_title"]
        if "cv_intro" in site_data["about"]:
            site_data["about"]["intro"] = site_data["about"]["cv_intro"]

        rendered_html = render_template(
            "cv.html",
            lang=lang,
            about=site_data["about"],
            ui_text=site_data["ui_text"],
            education=site_data["education"],
            experience=site_data["experience"],
            projects=site_data["projects"],
            publications=site_data["publications"],
            social_links=site_data["social_links"],
            skills=site_data.get("skills", []),
            languages=site_data.get("languages", []),
        )

        pdf = HTML(string=rendered_html).write_pdf()

        return (
            pdf,
            200,
            {
                "Content-Type": "application/pdf",
                "Content-Disposition": 'inline; filename="Fabricio_Mendoza_CV.pdf"',
            },
        )

    @app.route("/<lang>/blog/")
    def blog(lang):
        session["lang"] = lang
        _set_locale(lang)
        site_data = load_site_data(app.config["DB"], lang)
        ui_text = site_data["ui_text"]

        posts = [
            p for p in flatpages if p.path.startswith(lang + "/") and "date" in p.meta
        ]
        posts.sort(key=lambda item: item.meta["date"], reverse=True)
        return render_template("blog.html", lang=lang, posts=posts, ui_text=ui_text)

    @app.route("/<lang>/blog/<path:path>/")
    def post(lang, path):
        session["lang"] = lang
        _set_locale(lang)
        site_data = load_site_data(app.config["DB"], lang)
        ui_text = site_data["ui_text"]

        full_path = f"{lang}/{path}"
        post_obj = flatpages.get_or_404(full_path)
        return render_template("post.html", lang=lang, post=post_obj, ui_text=ui_text)

    @app.route("/pygments.css")
    def pygments_css():
        return pygments_style_defs("tango"), 200, {"Content-Type": "text/css"}

    @app.route("/api/update-portfolio", methods=["POST"])
    @login_required
    def update_portfolio():
        data = request.get_json()

        collection_name = data.get("collection")
        doc_id = data.get("id")
        field = data.get("field")
        lang = data.get("lang")
        nuevo_texto = data.get("text")

        if not collection_name or not field or not lang:
            return jsonify({"status": "error", "message": "Datos incompletos"}), 400

        db = app.config["DB"]
        collection = db[collection_name]
        user_id = current_user.id

        try:
            if collection_name in ["about_me", "portfolio_global"]:
                campo_a_actualizar = f"translations.{lang}.{field}"
                result = collection.update_one(
                    {"user_id": user_id}, {"$set": {campo_a_actualizar: nuevo_texto}}
                )
            else:
                id_key_map = {
                    "projects": "project_id",
                    "experience": "experience_id",
                    "education": "education_id",
                    "publications": "publication_id",
                }
                id_key = id_key_map.get(collection_name)
                campo_a_actualizar = f"translations.{lang}.{field}"

                result = collection.update_one(
                    {"user_id": user_id, id_key: doc_id},
                    {"$set": {campo_a_actualizar: nuevo_texto}},
                )

            if result.modified_count > 0 or result.matched_count > 0:
                return jsonify(
                    {"status": "success", "message": "Actualizado correctamente"}
                )
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": "No se encontró el registro para actualizar",
                    }
                ), 404

        except PyMongoError as e:
            app.logger.error(f"Error actualizando la BD: {e!s}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
