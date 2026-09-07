from app.core.database import get_database
from app.core.security import get_current_user
from app.models.profile import ProfileResponse, ProfileUpdate
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/profile", tags=["Perfil"])


# 🔓 RUTA PÚBLICA (Guest): Consulta de la colección `about_me`
@router.get("", response_model=ProfileResponse)
async def get_profile():
    """Devuelve la información pública del perfil (colección about_me)."""
    db = get_database()
    about_collection = db["about_me"]

    profile_data = await about_collection.find_one({})

    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado.",
        )

    profile_data["id"] = str(profile_data["_id"])
    if "user_id" in profile_data:
        profile_data["user_id"] = str(profile_data["user_id"])

    return ProfileResponse(**profile_data)


# 🔒 RUTA PROTEGIDA (Admin): Modificación con Token JWT
@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_update: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Actualiza la información de la colección about_me. Requiere autenticación."""
    db = get_database()
    about_collection = db["about_me"]

    update_data = {
        k: v
        for k, v in profile_update.model_dump().items()
        if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos válidos para actualizar.",
        )

    user_id = current_user["_id"]

    result = await about_collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_data},
        upsert=True,
        return_document=True,
    )

    result["id"] = str(result["_id"])
    result["user_id"] = str(result["user_id"])

    return ProfileResponse(**result)