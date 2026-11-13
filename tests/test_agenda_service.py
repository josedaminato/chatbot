from datetime import date, time
from unittest.mock import patch

import pytest

from app.schemas.turno_schema import EstadoTurno, TurnoCreate
from app.services.agenda_service import AgendaService


@pytest.fixture
def agenda_service():
    return AgendaService()


@pytest.fixture
def turno_data():
    return TurnoCreate(
        phone_number="TEST_PHONE_001",
        patient_name="TEST PATIENT",
        appointment_date=date.today(),
        appointment_time=time(14, 30),
        urgency_level="normal",
        notes="TEST NOTE",
    )


@patch("app.services.agenda_service.create_appointment", return_value=1)
@patch(
    "app.services.agenda_service.AgendaService._check_availability", return_value=True
)
def test_create_appointment_success(
    mock_check, mock_create, agenda_service, turno_data
):
    result = agenda_service.create_appointment(turno_data)
    assert result["success"] is True
    assert "appointment_id" in result


@patch("app.services.agenda_service.get_appointment", return_value=None)
def test_get_appointment_not_found(mock_get, agenda_service):
    result = agenda_service.get_appointment(999)
    assert result is None


@patch(
    "app.services.agenda_service.get_appointment",
    return_value={
        "id": 1,
        "phone_number": "TEST_VALUE",
        "patient_name": "TEST_VALUE",
        "appointment_date": date.today(),
        "appointment_time": time(14, 30),
        "urgency_level": "TEST_VALUE",
        "notes": "TEST_VALUE",
        "status": EstadoTurno.PENDIENTE,
        "created_at": "TEST_VALUE",
        "updated_at": "TEST_VALUE",
    },
)
def test_get_appointment_found(mock_get, agenda_service):
    result = agenda_service.get_appointment(1)
    assert result is not None
    assert result["id"] == 1
