from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGO_URI)
    print("✅ Conexión establecida con MongoDB vía Motor (Async)")


async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("❌ Conexión con MongoDB cerrada")


def get_database():
    return db.client[settings.DB_NAME]