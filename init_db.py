import os
import sys
import bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables del archivo .env para la conexión a Atlas
load_dotenv(override=True)

def create_admin_user():
    # 1. Validar que el usuario haya pasado los argumentos en la terminal
    if len(sys.argv) < 3:
        print("\n[ERROR] Faltan parámetros.")
        print("Uso correcto: python init_db.py <usuario_admin> <contraseña_admin>")
        print("Ejemplo:     python init_db.py fabricio MiClaveSegura123\n")
        return

    # Capturamos los datos directamente desde la consola
    admin_username = sys.argv[1]
    admin_password = sys.argv[2]

    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        print("[ERROR] No se encontró la variable MONGO_URI en el archivo .env")
        return

    # Conectar a MongoDB Atlas
    client = MongoClient(mongo_uri)
    db = client['personal_webpage']
    users_collection = db['users']

    # Verificar si el usuario ya existe
    existing_user = users_collection.find_one({'username': admin_username})
    if existing_user:
        print(f"[AVISO] El usuario '{admin_username}' ya existe en MongoDB Atlas.")
        return

    # Encriptar la contraseña
    password_bytes = admin_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # Crear el documento
    admin_document = {
        "username": admin_username,
        "password_hash": hashed_password
    }

    # Insertar en la nube
    result = users_collection.insert_one(admin_document)
    print(f"\n[ÉXITO] ¡Usuario '{admin_username}' creado correctamente en MongoDB Atlas!")
    print(f"ID en la nube: {result.inserted_id}\n")

if __name__ == '__main__':
    create_admin_user()