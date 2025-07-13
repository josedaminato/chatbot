"""
Schemas para turnos usando Pydantic
Validaciones y documentación de estructuras de datos
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time
from enum import Enum

class EstadoTurno(str, Enum):
    """Estados posibles de un turno"""
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    COMPLETADO = "completado"
    AUSENTE = "ausente"

class TurnoBase(BaseModel):
    """Schema base para turnos"""
    phone_number: str = Field(..., description="Número de teléfono del paciente")
    patient_name: Optional[str] = Field(None, description="Nombre del paciente")
    appointment_date: date = Field(..., description="Fecha del turno")
    appointment_time: time = Field(..., description="Hora del turno")
    urgency_level: Optional[str] = Field(None, description="Nivel de urgencia")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        """Valida formato de número de teléfono"""
        if not v or len(v) < 10:
            raise ValueError('Número de teléfono inválido')
        return v
    
    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v):
        """Valida que la fecha no sea en el pasado"""
        from datetime import date
        if v < date.today():
            raise ValueError('La fecha del turno no puede ser en el pasado')
        return v

class TurnoCreate(TurnoBase):
    """Schema para crear un nuevo turno"""
    pass

class TurnoUpdate(BaseModel):
    """Schema para actualizar un turno existente"""
    phone_number: Optional[str] = None
    patient_name: Optional[str] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    urgency_level: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[EstadoTurno] = None

class TurnoResponse(TurnoBase):
    """Schema para respuesta de turno"""
    id: int = Field(..., description="ID único del turno")
    status: EstadoTurno = Field(..., description="Estado actual del turno")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: Optional[str] = Field(None, description="Fecha de última actualización")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "phone_number": "+5491112345678",
                "patient_name": "Juan Pérez",
                "appointment_date": "2024-01-15",
                "appointment_time": "14:30:00",
                "urgency_level": "normal",
                "notes": "Primera consulta",
                "status": "pendiente",
                "created_at": "2024-01-10T10:00:00Z",
                "updated_at": "2024-01-10T10:00:00Z"
            }
        }
    }

class TurnoListResponse(BaseModel):
    """Schema para lista de turnos"""
    turnos: List[TurnoResponse] = Field(..., description="Lista de turnos")
    total: int = Field(..., description="Total de turnos")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Turnos por página") 

# Alias para compatibilidad y claridad
TurnoSchema = TurnoCreate 