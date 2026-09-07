from contextlib import asynccontextmanager
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.portfolio import router as portfolio_router
from app.core.config import settings
from app.core.database import close_mongo_connection, connect_to_mongo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicio del servidor: conectar a MongoDB
    await connect_to_mongo()
    yield
    # Apagado del servidor: cerrar conexión con MongoDB
    await close_mongo_connection()


app = FastAPI(
    title="Personal Webpage & AI CV Platform",
    version="2.0.0",
    lifespan=lifespan,
)

# Configuración de CORS para permitir peticiones desde React/Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar los routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "framework": "FastAPI"}