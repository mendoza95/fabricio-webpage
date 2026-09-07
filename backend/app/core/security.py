from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.database import get_database
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

# Algoritmo de encriptación simétrica para el token
ALGORITHM = "HS256"
# Duración del token de acceso (ejemplo: 24 horas)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

security_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Genera un token JWT firmado criptográficamente con tiempo de expiración."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    auth: HTTPAuthorizationCredentials | None = Depends(security_scheme),
):
    """Dependencia para proteger rutas administrativas.

    Si no hay token o es inválido, rechaza la petición con error 401.
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación para realizar esta acción.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.credentials  # Extrae el texto del JWT token

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido.",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de acceso ha expirado. Por favor, inicia sesión de nuevo.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales.",
        )

    db = get_database()
    user = await db["users"].find_one({"username": username})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
        )

    return user
