import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from pymongo import MongoClient
from bson.objectid import ObjectId
from bcrypt import checkpw
from dotenv import load_dotenv

# Creamos el Blueprint
auth_bp = Blueprint('auth', __name__)

# 1. Cargar las variables de entorno del archivo .env
load_dotenv(override=True)

# 2. Leer la URI desde el entorno
MONGO_URI = os.environ.get('MONGO_URI')

if not MONGO_URI:
    raise ValueError("¡ERROR CRÍTICO: La variable MONGO_URI no está definida en el archivo .env!")

# 3. INSTANCIAR EL CLIENTE UNA SOLA VEZ (Mejor práctica / Connection Pooling)
# PyMongo gestionará automáticamente un grupo de conexiones reutilizables hacia Atlas.
client = MongoClient(MONGO_URI)
db = client['personal_webpage']

class User():
    # Implementamos los métodos de UserMixin manualmente para no depender de la app central aquí
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def is_authenticated(self): return True
    def is_active(self): return True
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

def get_db_collection():
    """
    Retorna la colección de usuarios reutilizando la instancia del cliente global.
    """
    return db['users']

# El user_loader ahora vive aquí
def load_user_from_db(user_id):
    if user_id == 'guest':
        return None
    try:
        users_collection = get_db_collection()
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            return User(user['_id'], user['username'])
    except Exception:
        return None
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_collection = get_db_collection()
        user = users_collection.find_one({'username': username})

        if user and checkpw(password.encode(), user['password_hash']):
            user_obj = User(str(user['_id']), user['username'])
            login_user(user_obj)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index', lang=session.get('lang', 'en')))
        else:
            flash('Invalid username or password.', 'danger')
            # CAMBIA EL RENDER POR UNA REDIRECCIÓN:
            return redirect(url_for('index', lang=session.get('lang', 'en')))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index', lang=session.get('lang', 'en')))