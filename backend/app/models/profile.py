from pydantic import BaseModel, Field


class LanguageSkill(BaseModel):
    name: dict[str, str] = Field(default_factory=dict)
    level: dict[str, str] = Field(default_factory=dict)


class AboutTranslation(BaseModel):
    title: str = ""
    intro: list[str] = Field(default_factory=list)
    cv_title: str = ""
    cv_intro: list[str] = Field(
        default_factory=list
    )  # 👈 Cambiado de str a list[str]
    cv_button: str = ""


class TranslationsMap(BaseModel):
    es: AboutTranslation = Field(default_factory=AboutTranslation)
    en: AboutTranslation = Field(default_factory=AboutTranslation)


class ProfileBase(BaseModel):
    profile_image: str = ""
    profile_image_alt: dict[str, str] = Field(default_factory=dict)
    cv_filename: str = ""
    languages: list[LanguageSkill] = Field(default_factory=list)
    translations: TranslationsMap = Field(default_factory=TranslationsMap)


class ProfileResponse(ProfileBase):
    id: str | None = None
    user_id: str | None = None


class ProfileUpdate(BaseModel):
    profile_image: str | None = None
    profile_image_alt: dict[str, str] | None = None
    cv_filename: str | None = None
    languages: list[LanguageSkill] | None = None
    translations: TranslationsMap | None = None