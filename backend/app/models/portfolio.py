from pydantic import BaseModel, Field

# --- PROYECTOS ---
class ProjectTranslation(BaseModel):
    name: str = ""
    description: str = ""
    description_cv: list[str] = Field(default_factory=list)  # 👈 Cambiado a list[str]

class ProjectBase(BaseModel):
    project_id: str | None = None
    image: str = ""
    technologies: list[str] = Field(default_factory=list)
    live_url: str | None = None  # 👈 Permite None si no hay URL activa
    github_urls: list[str] = Field(default_factory=list)
    translations: dict[str, ProjectTranslation] = Field(default_factory=dict)

class ProjectResponse(ProjectBase):
    id: str | None = None
    user_id: str | None = None

# --- EXPERIENCIA ---
class ExperienceTranslation(BaseModel):
    role: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    description_cv: list[str] = Field(default_factory=list)  # 👈 Cambiado a list[str]

class ExperienceBase(BaseModel):
    experience_id: str | None = None
    company_logo: str = ""
    company_url: str = ""
    start_date: str = ""
    end_date: str = ""
    translations: dict[str, ExperienceTranslation] = Field(default_factory=dict)

class ExperienceResponse(ExperienceBase):
    id: str | None = None
    user_id: str | None = None

# --- EDUCACIÓN ---
class EducationTranslation(BaseModel):
    degree: str = ""
    institution: str = ""
    location: str = ""
    description: str = ""

class EducationBase(BaseModel):
    education_id: str | None = None
    institution_logo: str = ""
    institution_url: str = ""
    start_year: int | str = ""  # 👈 Acepta int o str
    end_year: int | str = ""    # 👈 Acepta int o str
    translations: dict[str, EducationTranslation] = Field(default_factory=dict)

class EducationResponse(EducationBase):
    id: str | None = None
    user_id: str | None = None

# --- PUBLICACIONES ---
class PublicationTranslation(BaseModel):
    title: str = ""
    journal: str = ""
    journal_cv: str = ""

class PublicationBase(BaseModel):
    publication_id: str | None = None
    authors: str = ""
    year: int | str = ""  # 👈 Acepta int o str
    urls: list[str] = Field(default_factory=list)
    translations: dict[str, PublicationTranslation] = Field(default_factory=dict)

class PublicationResponse(PublicationBase):
    id: str | None = None
    user_id: str | None = None
    

# --- PORTAFOLIO GLOBAL (portfolio_global) ---

class SkillItem(BaseModel):
    en: str = ""
    es: str = ""

class SocialMediaItem(BaseModel):
    name: str = ""
    url: str = ""
    username: str = ""
    icon_svg: str = ""

class PortfolioGlobalResponse(BaseModel):
    id: str | None = None
    user_id: str | None = None
    skills: list[SkillItem] = Field(default_factory=list)
    social_media: list[SocialMediaItem] = Field(default_factory=list)

class PortfolioGlobalUpdate(BaseModel):
    skills: list[SkillItem] | None = None
    social_media: list[SocialMediaItem] | None = None


# --- TRADUCCIONES DE LA INTERFAZ (ui_translations) ---

class UiTextDict(BaseModel):
    education_title: str = ""
    experience_title: str = ""
    projects_title: str = ""
    publications_title_cv: str = ""
    publications_title: str = ""
    news_title: str = ""
    contact_title: str = ""
    no_experience_message: str = ""
    no_publications_message: str = ""
    no_news_message: str = ""
    technologies_label: str = ""
    live_demo_button: str = ""
    github_repo_button: str = ""
    published_on_prefix: str = ""
    date_format: str = ""
    view_all_posts_button: str = ""
    blog_title: str = ""
    publication_link_text: str = ""
    all_posts_title: str = ""
    no_posts_found: str = ""
    languages_cv: str = ""
    profile_cv: str = ""
    contact_cv: str = ""
    skills_cv: str = ""

class UiTranslationsResponse(BaseModel):
    id: str | None = None
    translations: dict[str, UiTextDict] = Field(default_factory=dict)