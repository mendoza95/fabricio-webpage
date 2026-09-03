from bcrypt import checkpw
from bson.objectid import ObjectId
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)
from flask_login import UserMixin, login_required, login_user, logout_user
from pymongo.errors import PyMongoError

auth_bp = Blueprint("auth", __name__)


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


def get_db_collection():
    """Obtiene la colección 'users' desde la instancia dinámica de la app en ejecución."""
    db = current_app.config["DB"]
    return db["users"]


def load_user_from_db(user_id):
    if user_id == "guest":
        return None
    try:
        users_collection = get_db_collection()
        user = users_collection().find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user["_id"], user["username"])
    except PyMongoError:
        return None
    return None


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    users_collection = get_db_collection()
    user_data = users_collection.find_one({"username": username})

    if not user_data or "password_hash" not in user_data:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Usuario o contraseña incorrectos.",
                }
            ),
            401,
        )

    password_bytes = password.encode("utf-8")
    stored_hash = user_data["password_hash"]
    hash_bytes = (
        stored_hash.encode("utf-8")
        if isinstance(stored_hash, str)
        else bytes(stored_hash)
    )

    if checkpw(password_bytes, hash_bytes):
        # 1. Crear la instancia de usuario
        user_obj = User(user_data)

        # 2. Registrar la sesión en Flask-Login
        login_user(user_obj, remember=True)

        return jsonify({"success": True, "message": "Inicio de sesión exitoso."})

    return (
        jsonify(
            {"success": False, "message": "Usuario o contraseña incorrectos."}
        ),
        401,
    )


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index", lang=session.get("lang", "en")))
