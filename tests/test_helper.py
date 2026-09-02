from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from helper import _parse_date_flexible, load_site_data

BOGOTA_TZ = ZoneInfo("America/Bogota")


def test_parse_date_flexible_valid_formats():
    """Prueba que los formatos válidos se conviertan correctamente a datetime."""
    d1 = _parse_date_flexible("2024-05-10")
    d2 = _parse_date_flexible("10-05-2024")
    d3 = _parse_date_flexible("May 10, 2024")

    assert d1 == datetime(2024, 5, 10, tzinfo=BOGOTA_TZ)
    assert d2 == datetime(2024, 5, 10, tzinfo=BOGOTA_TZ)
    assert d3 == datetime(2024, 5, 10, tzinfo=BOGOTA_TZ)


def test_parse_date_flexible_invalid_format():
    """Prueba que un formato inválido devuelva la fecha por defecto (1970-01-01) sin romper el programa."""
    invalid_date = _parse_date_flexible("fecha-invalida-123")
    assert invalid_date == datetime(1970, 1, 1, tzinfo=BOGOTA_TZ)


def test_load_site_data_empty_db_raises_error(mock_db):
    """Prueba que load_site_data lance un RuntimeError si no hay usuario en la BD."""
    with pytest.raises(RuntimeError) as exc_info:
        load_site_data(mock_db, "en")

    assert "No se encontró ningún usuario configurado" in str(exc_info.value)


def test_load_site_data_success(mock_db):
    """Prueba la extracción e idioma correcto cargando un usuario y portfolio de prueba."""
    # 1. Poblar la BD falsa con datos mínimos requeridos
    user_id = mock_db["users"].insert_one({"username": "fabricio"}).inserted_id

    mock_db["about_me"].insert_one(
        {
            "user_id": user_id,
            "translations": {
                "es": {"title": "Hola, soy Fabricio"},
                "en": {"title": "Hi, I am Fabricio"},
            },
        }
    )

    # 2. Invocamos la función con idioma español
    data_es = load_site_data(mock_db, "es")
    assert data_es["about"]["title"] == "Hola, soy Fabricio"

    # 3. Invocamos la función con idioma inglés
    data_en = load_site_data(mock_db, "en")
    assert data_en["about"]["title"] == "Hi, I am Fabricio"
