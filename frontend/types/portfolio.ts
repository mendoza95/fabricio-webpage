// 0. Objeto Bilingüe reutilizable
export interface LocalizedString {
    en: string;
    es: string;
}

// ==========================================
// SECTION: ABOUT ME
// ==========================================

// A. Traducción principal de la sección About Me
export interface AboutMeTranslation {
    title: string;
    intro: string[];
    cv_title: string;
    cv_intro: string[];
    cv_button: string;
}

// B. Estructura de cada Idioma en la lista
export interface LanguageItem {
    name: LocalizedString;
    level: LocalizedString;
    note: LocalizedString;
}

// C. Modelo Base
export interface AboutMeBase {
    profile_image: string;
    profile_image_alt: LocalizedString;
    cv_filename: string;
    languages: LanguageItem[];
    translations: Record<string, AboutMeTranslation>;
}

// D. Modelo de Respuesta completo
export interface AboutMeResponse extends AboutMeBase {
    id?: string;
    user_id?: string;
}

// ==========================================
// SECTION: PROJECTS
// ==========================================

export interface ProjectTranslation {
    name: string;
    description: string;
    description_cv: string[];
}

export interface ProjectBase {
    project_id?: string | null;
    image: string;
    technologies: string[];
    live_url?: string | null;
    github_urls: string[];
    translations: Record<string, ProjectTranslation>;
}

export interface ProjectResponse extends ProjectBase {
    id?: string;
    user_id?: string;
}

// ==========================================
// SECTION: EXPERIENCE
// ==========================================

export interface ExperienceTranslation {
    role: string;
    company: string;
    location: string;
    description: string;
    description_cv: string[];
}

export interface ExperienceBase {
    experience_id?: string | null;
    company_logo: string;
    company_url: string;
    start_date: string;
    end_date: string;
    translations: Record<string, ExperienceTranslation>;
}

export interface ExperienceResponse extends ExperienceBase {
    id?: string;
    user_id?: string;
}

// ==========================================
// SECTION: EDUCATION
// ==========================================

export interface EducationTranslation {
    degree: string;
    institution: string;
    location: string;
    description: string;
    description_cv: string[];
}

export interface EducationBase {
    education_id?: string | null;
    institution_logo: string;
    institution_url: string;
    start_year: number | string;
    end_year: number | string;
    translations: Record<string, EducationTranslation>;
}

export interface EducationResponse extends EducationBase {
    id?: string;
    user_id?: string;
}

// ==========================================
// SECTION: PUBLICATIONS
// ==========================================

export interface PublicationTranslation {
    title: string;
    journal: string;
    journal_cv: string;
}

export interface PublicationBase {
    publication_id?: string | null;
    authors: string;
    year: number | string;
    urls: string[];
    translations: Record<string, PublicationTranslation>;
}

export interface PublicationResponse extends PublicationBase {
    id?: string;
    user_id?: string;
}

// ==========================================
// SECTION: PORTFOLIO GLOBAL
// ==========================================

export interface SkillItem {
    en: string;
    es: string;
}

export interface SocialMediaItem {
    name: string;
    url: string;
    username: string;
    icon_svg: string;
}

export interface PortfolioGlobalBase {
    skills: SkillItem[];
    social_media: SocialMediaItem[];
}

export interface PortfolioGlobalResponse extends PortfolioGlobalBase {
    id?: string;
    user_id?: string;
}

// ==========================================
// SECTION: UI TRANSLATIONS
// ==========================================

export interface UiTextDict {
    education_title: string;
    experience_title: string;
    projects_title: string;
    publications_title_cv: string;
    publications_title: string;
    news_title: string;
    contact_title: string;
    no_experience_message: string;
    no_publications_message: string;
    no_news_message: string;
    technologies_label: string;
    live_demo_button: string;
    github_repo_button: string;
    published_on_prefix: string;
    date_format: string;
    view_all_posts_button: string;
    blog_title: string;
    publication_link_text: string;
    all_posts_title: string;
    no_posts_found: string;
    languages_cv: string;
    profile_cv: string;
    contact_cv: string;
    skills_cv: string;
}

export interface UiTranslationsResponse {
    id?: string | null;
    translations: Record<string, UiTextDict>;
}