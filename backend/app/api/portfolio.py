from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.core.database import get_database
from app.core.security import get_current_user
from app.models.portfolio import (
    ProjectBase, ProjectResponse,
    ExperienceBase, ExperienceResponse,
    EducationBase, EducationResponse,
    PublicationBase, PublicationResponse,
    PortfolioGlobalUpdate, PortfolioGlobalResponse, 
    UiTranslationsResponse
)

router = APIRouter(prefix="/portfolio", tags=["Portafolio"])


# Helper para convertir ObjectId a String de forma limpia
def format_doc(doc: dict) -> dict:
    doc["id"] = str(doc["_id"])
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    return doc


# ==========================================
# 1. PROYECTOS
# ==========================================

@router.get("/projects", response_model=list[ProjectResponse])
async def get_projects():
    """Obtiene la lista de proyectos públicos."""
    db = get_database()
    projects = await db["projects"].find().to_list(100)
    return [format_doc(p) for p in projects]


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectBase, current_user: dict = Depends(get_current_user)):
    """Crea un nuevo proyecto (Requiere Token)."""
    db = get_database()
    doc = project.model_dump()
    doc["user_id"] = current_user["_id"]
    
    result = await db["projects"].insert_one(doc)
    created_project = await db["projects"].find_one({"_id": result.inserted_id})
    return format_doc(created_project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_data: ProjectBase, current_user: dict = Depends(get_current_user)):
    """Actualiza un proyecto existente (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="ID de proyecto no válido")
    
    update_data = {k: v for k, v in project_data.model_dump().items() if v is not None}
    
    result = await db["projects"].find_one_and_update(
        {"_id": ObjectId(project_id)},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
    return format_doc(result)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Elimina un proyecto (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="ID de proyecto no válido")
    
    result = await db["projects"].delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return None


# ==========================================
# 2. EXPERIENCIA
# ==========================================

@router.get("/experience", response_model=list[ExperienceResponse])
async def get_experience():
    """Obtiene la lista de experiencia laboral."""
    db = get_database()
    experiences = await db["experience"].find().to_list(100)
    return [format_doc(e) for e in experiences]


@router.post("/experience", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(experience: ExperienceBase, current_user: dict = Depends(get_current_user)):
    """Crea una nueva experiencia laboral (Requiere Token)."""
    db = get_database()
    doc = experience.model_dump()
    doc["user_id"] = current_user["_id"]
    
    result = await db["experience"].insert_one(doc)
    created_exp = await db["experience"].find_one({"_id": result.inserted_id})
    return format_doc(created_exp)


@router.put("/experience/{exp_id}", response_model=ExperienceResponse)
async def update_experience(exp_id: str, exp_data: ExperienceBase, current_user: dict = Depends(get_current_user)):
    """Actualiza una experiencia laboral (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(exp_id):
        raise HTTPException(status_code=400, detail="ID de experiencia no válido")
    
    update_data = {k: v for k, v in exp_data.model_dump().items() if v is not None}
    
    result = await db["experience"].find_one_and_update(
        {"_id": ObjectId(exp_id)},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Experiencia no encontrada")
        
    return format_doc(result)


@router.delete("/experience/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(exp_id: str, current_user: dict = Depends(get_current_user)):
    """Elimina una experiencia laboral (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(exp_id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    result = await db["experience"].delete_one({"_id": ObjectId(exp_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Experiencia no encontrada")
    return None


# ==========================================
# 3. EDUCACIÓN
# ==========================================

@router.get("/education", response_model=list[EducationResponse])
async def get_education():
    """Obtiene la lista de educación."""
    db = get_database()
    education_list = await db["education"].find().to_list(100)
    return [format_doc(e) for e in education_list]


@router.post("/education", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def create_education(education: EducationBase, current_user: dict = Depends(get_current_user)):
    """Agrega un registro de educación (Requiere Token)."""
    db = get_database()
    doc = education.model_dump()
    doc["user_id"] = current_user["_id"]
    
    result = await db["education"].insert_one(doc)
    created_edu = await db["education"].find_one({"_id": result.inserted_id})
    return format_doc(created_edu)


@router.put("/education/{edu_id}", response_model=EducationResponse)
async def update_education(edu_id: str, edu_data: EducationBase, current_user: dict = Depends(get_current_user)):
    """Actualiza un registro de educación (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(edu_id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    update_data = {k: v for k, v in edu_data.model_dump().items() if v is not None}
    
    result = await db["education"].find_one_and_update(
        {"_id": ObjectId(edu_id)},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Educación no encontrada")
        
    return format_doc(result)


@router.delete("/education/{edu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(edu_id: str, current_user: dict = Depends(get_current_user)):
    """Elimina un registro de educación (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(edu_id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    result = await db["education"].delete_one({"_id": ObjectId(edu_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registro de educación no encontrado")
    return None


# ==========================================
# 4. PUBLICACIONES
# ==========================================

@router.get("/publications", response_model=list[PublicationResponse])
async def get_publications():
    """Obtiene la lista de publicaciones."""
    db = get_database()
    publications = await db["publications"].find().to_list(100)
    return [format_doc(p) for p in publications]


@router.post("/publications", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(publication: PublicationBase, current_user: dict = Depends(get_current_user)):
    """Crea una publicación (Requiere Token)."""
    db = get_database()
    doc = publication.model_dump()
    doc["user_id"] = current_user["_id"]
    
    result = await db["publications"].insert_one(doc)
    created_pub = await db["publications"].find_one({"_id": result.inserted_id})
    return format_doc(created_pub)


@router.put("/publications/{pub_id}", response_model=PublicationResponse)
async def update_publication(pub_id: str, pub_data: PublicationBase, current_user: dict = Depends(get_current_user)):
    """Actualiza una publicación (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(pub_id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    update_data = {k: v for k, v in pub_data.model_dump().items() if v is not None}
    
    result = await db["publications"].find_one_and_update(
        {"_id": ObjectId(pub_id)},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
        
    return format_doc(result)


@router.delete("/publications/{pub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(pub_id: str, current_user: dict = Depends(get_current_user)):
    """Elimina una publicación (Requiere Token)."""
    db = get_database()
    if not ObjectId.is_valid(pub_id):
        raise HTTPException(status_code=400, detail="ID no válido")
    
    result = await db["publications"].delete_one({"_id": ObjectId(pub_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return None


# ==========================================
# 5. PORTAFOLIO GLOBAL (PROTEGIDO)
# ==========================================

@router.get("/global", response_model=PortfolioGlobalResponse)
async def get_portfolio_global(current_user: dict = Depends(get_current_user)):
    """Obtiene habilidades y redes sociales (Requiere Token)."""
    db = get_database()
    global_doc = await db["portfolio_global"].find_one()
    if not global_doc:
        raise HTTPException(status_code=404, detail="Configuración global no encontrada")
    return format_doc(global_doc)


@router.put("/global", response_model=PortfolioGlobalResponse)
async def update_portfolio_global(
    global_data: PortfolioGlobalUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """Actualiza habilidades o redes sociales (Requiere Token)."""
    db = get_database()
    update_fields = {k: v for k, v in global_data.model_dump().items() if v is not None}
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="Debe proporcionar 'skills' o 'social_media'")

    global_doc = await db["portfolio_global"].find_one()
    if not global_doc:
        raise HTTPException(status_code=404, detail="Configuración global no encontrada")

    result = await db["portfolio_global"].find_one_and_update(
        {"_id": global_doc["_id"]},
        {"$set": update_fields},
        return_document=True
    )
    return format_doc(result)


# ==========================================
# 6. TRADUCCIONES DE LA INTERFAZ (SOLO LECTURA PÚBLICA)
# ==========================================

@router.get("/ui-translations", response_model=UiTranslationsResponse)
async def get_ui_translations():
    """Obtiene las traducciones globales de la interfaz (Público, Solo Lectura)."""
    db = get_database()
    ui_doc = await db["ui_translations"].find_one()
    if not ui_doc:
        raise HTTPException(status_code=404, detail="Traducciones no encontradas")
    return format_doc(ui_doc)