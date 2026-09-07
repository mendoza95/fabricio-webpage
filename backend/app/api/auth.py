import bcrypt
from app.core.database import get_database
from app.core.security import create_access_token, get_current_user
from app.models.user import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    UserResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    db = get_database()
    users_collection = db["users"]

    user_data = await users_collection.find_one(
        {"username": credentials.username.strip()}
    )

    if not user_data or "password_hash" not in user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    password_bytes = credentials.password.encode("utf-8")
    stored_hash = user_data["password_hash"]
    hash_bytes = (
        stored_hash.encode("utf-8")
        if isinstance(stored_hash, str)
        else bytes(stored_hash)
    )

    if not bcrypt.checkpw(password_bytes, hash_bytes):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    # 🔑 Generar Token JWT
    access_token = create_access_token(data={"sub": user_data["username"]})

    return LoginResponse(
        success=True,
        message="Inicio de sesión exitoso.",
        token=TokenResponse(access_token=access_token),
        user=UserResponse(
            id=str(user_data["_id"]), username=user_data["username"]
        ),
    )


# 🔒 Ruta protegida: solo accesible con un token JWT válido
@router.get("/me", response_model=UserResponse)
async def get_authenticated_user(
    current_user: dict = Depends(get_current_user),
):
    """Devuelve la información del usuario actualmente autenticado."""
    return UserResponse(
        id=str(current_user["_id"]), username=current_user["username"]
    )