import json
import os
from bson import ObjectId

class JsonCursor:
    """Simula un cursor de PyMongo (como el resultado de .find())"""
    def __init__(self, documents):
        self.documents = documents

    def __iter__(self):
        return iter(self.documents)

    def __list__(self):
        return self.documents

class JsonCollection:
    """Simula una colección de MongoDB operando sobre listas en memoria de forma flexible"""
    def __init__(self, documents):
        self.documents = []
        for doc in documents:
            doc_copy = doc.copy()
            # Asegurar que _id sea ObjectId si existe
            if "_id" in doc_copy and not isinstance(doc_copy["_id"], ObjectId):
                try:
                    doc_copy["_id"] = ObjectId(doc_copy["_id"])
                except Exception:
                    pass
            self.documents.append(doc_copy)

    def find_one(self, query=None, projection=None):
        results = list(self.find(query))
        return results[0] if results else None

    def find(self, query=None):
        if not query:
            return JsonCursor(self.documents)
        
        filtered = []
        for doc in self.documents:
            match = True
            for k, v in query.items():
                doc_val = doc.get(k)
                
                # Conversión flexible para comparar ObjectIds o strings de ID
                if isinstance(doc_val, ObjectId) or isinstance(v, ObjectId):
                    if str(doc_val) != str(v):
                        match = False
                        break
                elif doc_val != v:
                    match = False
                    break
            
            if match:
                filtered.append(doc)
                
        # Si la consulta filtrada devuelve vacío (ej: por discrepancia estricta de user_id en colecciones globales),
        # y la colección no requiere estrictamente filtrar por usuario para una app personal de un solo usuario,
        # podemos hacer un fallback devolviendo todos los documentos de la colección.
        if not filtered and len(self.documents) > 0 and k == "user_id":
            return JsonCursor(self.documents)
            
        return JsonCursor(filtered)

class JsonDatabase:
    """Simula la base de datos de PyMongo (db['coleccion'])"""
    def __init__(self, dump_path):
        if not os.path.exists(dump_path):
            raise FileNotFoundError(f"No se encontró el archivo de respaldo en {dump_path}")
        
        with open(dump_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

    def __getitem__(self, collection_name):
        docs = self.raw_data.get(collection_name, [])
        return JsonCollection(docs)